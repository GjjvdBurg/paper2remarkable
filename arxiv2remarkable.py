#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Given an arXiv paper url this script:

1. Downloads the paper
2. Strips the timestamp
3. Crops the pdf to remove unnecessary borders
4. Shrinks the pdf to reduce the filesize
5. Renames it using the format:
    '_'.join(author_lastnames) + '_-_' + title + '_' + year.pdf
6. Uploads it to the reMarkable using rMapi.

Author: G.J.J. van den Burg
Date: 2019-02-02
License: MIT

"""

import PyPDF2
import argparse
import bs4
import os
import re
import requests
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse

from loguru import logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 "
    "Safari/537.36"
}


def exception(msg):
    print("ERROR: " + msg, file=sys.stderr)
    print("Error occurred. Exiting.", file=sys.stderr)
    raise SystemExit(1)


def arxiv_url(url):
    """Check if the url is to an arXiv page.

    >>> validate_url("https://arxiv.org/abs/1811.11242")
    True
    >>> validate_url("https://arxiv.org/pdf/1811.11242.pdf")
    True
    >>> validate_url("http://arxiv.org/abs/1811.11242")
    True
    >>> validate_url("http://arxiv.org/pdf/1811.11242.pdf")
    True
    >>> validate_url("https://arxiv.org/abs/1811.11242v1")
    True
    >>> validate_url("https://arxiv.org/pdf/1811.11242v1.pdf")
    True
    >>> validate_url("https://gertjanvandenburg.com")
    False
    """
    m = re.match(
        "https?://arxiv.org/(abs|pdf)/\d{4}\.\d{5}(v\d+)?(\.pdf)?", url
    )
    return not m is None


def valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False


def check_file_is_pdf(filename):
    try:
        PyPDF2.PdfFileReader(open(filename, "rb"))
        return True
    except PyPDF2.utils.PdfReadError:
        return False


def get_arxiv_urls(url):
    """Get the pdf and abs url from any given url """
    if re.match("https?://arxiv.org/abs/\d{4}\.\d{5}(v\d+)?", url):
        abs_url = url
        pdf_url = url.replace("abs", "pdf") + ".pdf"
    elif re.match("https?://arxiv.org/pdf/\d{4}\.\d{5}(v\d+)?\.pdf", url):
        abs_url = url[:-4].replace("pdf", "abs")
        pdf_url = url
    else:
        exception("Couldn't figure out arXiv urls.")
    return pdf_url, abs_url


def get_page_with_retry(url):
    """Get the content of an url, retrying up to five times on failure. """
    count = 0
    while True:
        res = requests.get(url, headers=HEADERS)
        if res.ok:
            logger.info("Downloading url: %s" % url)
            return res.content
        else:
            if count < 5:
                logger.info(
                    "Caught error for url %s. Retrying in 5 seconds." % url
                )
                time.sleep(5)
            else:
                exception("Failed to download url: %s" % url)


def download_url(url, filename):
    """Download the content of an url and save it to a filename """
    logger.info("Downloading file at url: %s" % url)
    content = get_page_with_retry(url)
    with open(filename, "wb") as fid:
        fid.write(content)


def dearxiv(input_file, pdftk_path="pdftk"):
    """Remove the arXiv timestamp from a pdf"""
    logger.info("Removing arXiv timestamp")
    basename = os.path.splitext(input_file)[0]
    uncompress_file = basename + "_uncompress.pdf"

    status = subprocess.call(
        [pdftk_path, input_file, "output", uncompress_file, "uncompress"]
    )
    if not status == 0:
        exception("pdftk failed to uncompress the pdf.")

    with open(uncompress_file, "rb") as fid:
        data = fid.read()
        # Remove the text element
        data = re.sub(
            b"\(arXiv:\d{4}\.\d{5}v\d\s+\[\w+\.\w+\]\s+\d{1,2}\s\w{3}\s\d{4}\)Tj",
            b"()Tj",
            data,
        )
        # Remove the URL element
        data = re.sub(
            b"<<\\n\/URI \(http://arxiv\.org/abs/\d{4}\.\d{5}v\d\)\\n\/S /URI\\n>>\\n",
            b"",
            data,
        )

    removed_file = basename + "_removed.pdf"
    with open(removed_file, "wb") as oid:
        oid.write(data)

    output_file = basename + "_dearxiv.pdf"
    status = subprocess.call(
        [pdftk_path, removed_file, "output", output_file, "compress"]
    )
    if not status == 0:
        exception("pdftk failed to compress the pdf.")

    return output_file


def crop_pdf(filepath, pdfcrop_path="pdfcrop"):
    logger.info("Cropping pdf file")
    status = subprocess.call(
        [pdfcrop_path, "--margins", "15 40 15 15", filepath],
        stdout=subprocess.DEVNULL,
    )
    if not status == 0:
        logger.warning("Failed to crop the pdf file at: %s" % filepath)
        return filepath
    cropped_file = os.path.splitext(filepath)[0] + "-crop.pdf"
    if not os.path.exists(cropped_file):
        logger.warning(
            "Can't find cropped file '%s' where expected." % cropped_file
        )
        return filepath
    return cropped_file


def shrink_pdf(filepath, gs_path="gs"):
    logger.info("Shrinking pdf file")
    output_file = os.path.splitext(filepath)[0] + "-shrink.pdf"
    status = subprocess.call(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/printer",
            "-dNOPAUSE",
            "-dBATCH",
            "-dQUIET",
            "-sOutputFile=%s" % output_file,
            filepath,
        ]
    )
    if not status == 0:
        logger.warning("Failed to shrink the pdf file")
        return filepath
    return output_file


def get_paper_info(url):
    logger.info("Getting paper info from arXiv")
    page = get_page_with_retry(url)
    soup = bs4.BeautifulSoup(page, "html.parser")
    authors = [
        x["content"] for x in soup.find_all("meta", {"name": "citation_author"})
    ]
    title = soup.find_all("meta", {"name": "citation_title"})[0]["content"]
    date = soup.find_all("meta", {"name": "citation_date"})[0]["content"]
    return dict(title=title, date=date, authors=authors)


def generate_filename(info):
    logger.info("Generating output filename")
    if len(info["authors"]) > 3:
        author_part = info["authors"][0].split(",")[0] + "_et_al"
    else:
        author_part = "_".join([x.split(",")[0] for x in info["authors"]])
    author_part = author_part.replace(" ", "_")
    title_part = info["title"].replace(",", "").replace(" ", "_")
    year_part = info["date"].split("/")[0]
    return author_part + "_-_" + title_part + "_" + year_part + ".pdf"


def upload_to_rm(filepath, remarkable_dir="/", rmapi_path="rmapi"):
    logger.info("Starting upload to reMarkable")
    status = subprocess.call(
        [rmapi_path, "put", filepath, remarkable_dir], stdout=subprocess.DEVNULL
    )
    if not status == 0:
        exception("Uploading file %s to remarkable failed" % filepath)
    logger.info("Upload successful.")


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-v", "--verbose", help="be verbose", action="store_true"
    )
    parser.add_argument(
        "-n",
        "--no-upload",
        help="don't upload to the reMarkable, save the output in current working dir",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="debug mode, doesn't upload to reMarkable",
        action="store_true",
    )
    parser.add_argument(
        "--filename",
        help="Filename to use for the file on reMarkable",
        default=None,
    )
    parser.add_argument(
        "--rmapi", help="path to rmapi executable", default="rmapi"
    )
    parser.add_argument(
        "--pdfcrop", help="path to pdfcrop executable", default="pdfcrop"
    )
    parser.add_argument(
        "--pdftk", help="path to pdftk executable", default="pdftk"
    )
    parser.add_argument("--gs", help="path to gs executable", default="gs")
    parser.add_argument(
        "input", help="url to an arxiv paper, url to pdf, or existing pdf file"
    )
    return parser.parse_args()


@logger.catch
def main():
    args = parse_args()

    if os.path.exists(args.input):
        mode = "local_file"
    elif arxiv_url(args.input):
        mode = "arxiv_url"
    elif valid_url(args.input):
        if args.filename is None:
            exception("Filename must be provided with pdf url (use --filename)")
        mode = "pdf_url"
    else:
        exception("Input not a valid url, arxiv url, or existing file.")

    if not args.verbose:
        logger.remove(0)

    start_wd = os.getcwd()

    with tempfile.TemporaryDirectory() as working_dir:
        if mode == "local_file":
            shutil.copy(args.input, working_dir)
            filename = os.path.basename(args.input)
            clean_filename = args.filename if args.filename else filename

        os.chdir(working_dir)
        if mode == "arxiv_url":
            pdf_url, abs_url = get_arxiv_urls(args.input)
            filename = "paper.pdf"
            download_url(pdf_url, filename)
            if args.filename:
                clean_filename = args.filename
            else:
                paper_info = get_paper_info(abs_url)
                clean_filename = generate_filename(paper_info)

        if mode == "pdf_url":
            filename = "paper.pdf"
            download_url(args.input, filename)
            if not check_file_is_pdf(filename):
                exception("Input url doesn't point to valid pdf file.")
            clean_filename = args.filename

        dearxived = dearxiv(filename, pdftk_path=args.pdftk)
        cropped = crop_pdf(dearxived, pdfcrop_path=args.pdfcrop)
        shrinked = shrink_pdf(cropped)
        shutil.move(shrinked, clean_filename)

        if args.debug:
            print("Paused in debug mode in dir: %s" % working_dir)
            print("Press enter to exit.")
            return input()

        if args.no_upload:
            if os.path.exists(os.path.join(start_wd, clean_filename)):
                tmpfname = os.path.splitext(filename)[0] + "_cropped.pdf"
                shutil.move(clean_filename, os.path.join(start_wd, tmpfname))
            else:
                shutil.move(clean_filename, start_wd)
        else:
            upload_to_rm(clean_filename, rmapi_path=args.rmapi)


if __name__ == "__main__":
    main()
