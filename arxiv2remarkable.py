#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.2.2"
__author__ = "G.J.J. van den Burg"

"""
Download a paper from various sources and send it to the reMarkable.

Author: G.J.J. van den Burg
Date: 2019-02-02
License: MIT

"""

import PyPDF2
import abc
import argparse
import bs4
import datetime
import os
import re
import requests
import shutil
import subprocess
import sys
import tempfile
import time
import titlecase
import urllib.parse

GITHUB_URL = "https://github.com/GjjvdBurg/arxiv2remarkable"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 "
    "Safari/537.36"
}

RM_WIDTH = 1404
RM_HEIGHT = 1872


class Provider(metaclass=abc.ABCMeta):
    """ ABC for providers of pdf sources """

    def __init__(
        self,
        verbose=False,
        upload=True,
        debug=False,
        center=False,
        blank=False,
        remarkable_dir="/",
        rmapi_path="rmapi",
        pdfcrop_path="pdfcrop",
        pdftk_path="pdftk",
        gs_path="gs",
    ):
        self.verbose = verbose
        self.upload = upload
        self.debug = debug
        self.center = center
        self.blank = blank
        self.remarkable_dir = remarkable_dir
        self.rmapi_path = rmapi_path
        self.pdfcrop_path = pdfcrop_path
        self.pdftk_path = pdftk_path
        self.gs_path = gs_path

        self.log("Starting %s" % type(self).__name__)

    def log(self, msg, mode="info"):
        if not self.verbose:
            return
        if not mode in ["info", "warning"]:
            raise ValueError("unknown logging mode.")
        now = datetime.datetime.now()
        print(
            now.strftime("%Y-%m-%d %H:%M:%S")
            + " - "
            + mode.upper()
            + " - "
            + msg
        )

    def warn(self, msg):
        self.log(msg, mode="warning")

    @staticmethod
    @abc.abstractmethod
    def validate(src):
        """ Validate whether ``src`` is appropriate for this provider """

    @abc.abstractmethod
    def retrieve_pdf(self, src, filename):
        """ Download pdf from src and save to filename """

    @abc.abstractmethod
    def get_paper_info(self, src):
        """ Retrieve the title/author (surnames)/year information """

    def create_filename(self, info, filename=None):
        """ Generate filename using the info dict or filename if provided """
        if not filename is None:
            return filename
        # we assume that the list of authors is surname only.
        self.log("Generating output filename")
        if len(info["authors"]) > 3:
            author_part = info["authors"][0] + "_et_al"
        else:
            author_part = "_".join(info["authors"])
        author_part = author_part.replace(" ", "_")
        title = info["title"].replace(",", "").replace(":", "")
        title_part = titlecase.titlecase(title).replace(" ", "_")
        year_part = info["date"].split("/")[0]
        name = author_part + "_-_" + title_part + "_" + year_part + ".pdf"
        self.log("Created filename: %s" % name)
        return name

    def center_pdf(self, filepath):
        if not self.center:
            return filepath
        pdf_file = PyPDF2.PdfFileReader(filepath)
        mediaBox = pdf_file.getPage(0).mediaBox
        width = mediaBox[2] - mediaBox[0]
        height = mediaBox[3] - mediaBox[1]
        padding = (height * RM_WIDTH - width * RM_HEIGHT) / RM_HEIGHT
        left_margin = padding / 2 + 15

        self.log("Centering PDF file")
        status = subprocess.call(
            [
                self.pdfcrop_path,
                "--margins",
                "%i 40 15 15" % left_margin,
                filepath,
            ],
            stdout=subprocess.DEVNULL,
        )
        if not status == 0:
            self.warn("Failed to crop the pdf file at: %s" % filepath)
            return filepath
        centered_file = os.path.splitext(filepath)[0] + "-crop.pdf"
        if not os.path.exists(centered_file):
            self.warn(
                "Can't find centered file '%s' where expected." % centered_file
            )
            return filepath
        return centered_file

    def blank_pdf(self, filepath):
        if not self.blank:
            return filepath

        self.log("Adding blank pages")
        input_pdf = PyPDF2.PdfFileReader(filepath)
        output_pdf = PyPDF2.PdfFileWriter()
        for page in input_pdf.pages:
            output_pdf.addPage(page)
            output_pdf.addBlankPage()

        output_file = os.path.splitext(filepath)[0] + "-blank.pdf"
        with open(output_file, "wb") as fp:
            output_pdf.write(fp)
        return output_file

    def crop_pdf(self, filepath):
        self.log("Cropping pdf file")
        status = subprocess.call(
            [self.pdfcrop_path, "--margins", "15 40 15 15", filepath],
            stdout=subprocess.DEVNULL,
        )
        if not status == 0:
            self.warn("Failed to crop the pdf file at: %s" % filepath)
            return filepath
        cropped_file = os.path.splitext(filepath)[0] + "-crop.pdf"
        if not os.path.exists(cropped_file):
            self.warn(
                "Can't find cropped file '%s' where expected." % cropped_file
            )
            return filepath
        return cropped_file

    def shrink_pdf(self, filepath):
        self.log("Shrinking pdf file")
        output_file = os.path.splitext(filepath)[0] + "-shrink.pdf"
        status = subprocess.call(
            [
                self.gs_path,
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
            self.warn("Failed to shrink the pdf file")
            return filepath
        return output_file

    def check_file_is_pdf(self, filename):
        try:
            fp = open(filename, "rb")
            pdf = PyPDF2.PdfFileReader(fp, strict=False)
            fp.close()
            del pdf
            return True
        except PyPDF2.utils.PdfReadError:
            exception("Downloaded file isn't a valid pdf file.")

    def download_url(self, url, filename):
        """Download the content of an url and save it to a filename """
        self.log("Downloading file at url: %s" % url)
        content = self.get_page_with_retry(url)
        with open(filename, "wb") as fid:
            fid.write(content)

    def get_page_with_retry(self, url, tries=5):
        count = 0
        while count < tries:
            count += 1
            error = False
            try:
                res = requests.get(url, headers=HEADERS)
            except requests.exceptions.ConnectionError:
                error = True
            if error or not res.ok:
                time.sleep(5)
                self.warn("Error getting url %s. Retrying in 5 seconds" % url)
                continue
            self.log("Downloading url: %s" % url)
            return res.content

    def upload_to_rm(self, filepath):
        remarkable_dir = self.remarkable_dir.rstrip("/")
        self.log("Starting upload to reMarkable")
        if remarkable_dir:
            status = subprocess.call(
                [self.rmapi_path, "mkdir", remarkable_dir],
                stdout=subprocess.DEVNULL,
            )
            if not status == 0:
                exception(
                    "Creating directory %s on reMarkable failed"
                    % remarkable_dir
                )
        status = subprocess.call(
            [self.rmapi_path, "put", filepath, remarkable_dir + "/"],
            stdout=subprocess.DEVNULL,
        )
        if not status == 0:
            exception("Uploading file %s to reMarkable failed" % filepath)
        self.log("Upload successful.")

    def dearxiv(self, input_file):
        """Remove the arXiv timestamp from a pdf"""
        self.log("Removing arXiv timestamp")
        basename = os.path.splitext(input_file)[0]
        uncompress_file = basename + "_uncompress.pdf"

        status = subprocess.call(
            [
                self.pdftk_path,
                input_file,
                "output",
                uncompress_file,
                "uncompress",
            ]
        )
        if not status == 0:
            exception("pdftk failed to uncompress the pdf.")

        with open(uncompress_file, "rb") as fid:
            data = fid.read()
            # Remove the text element
            data = re.sub(
                b"\(arXiv:\d{4}\.\d{4,5}v\d+\s+\[\w+\.\w+\]\s+\d{1,2}\s\w{3}\s\d{4}\)Tj",
                b"()Tj",
                data,
            )
            # Remove the URL element
            data = re.sub(
                b"<<\\n\/URI \(http://arxiv\.org/abs/\d{4}\.\d{4,5}v\d+\)\\n\/S /URI\\n>>\\n",
                b"",
                data,
            )

        removed_file = basename + "_removed.pdf"
        with open(removed_file, "wb") as oid:
            oid.write(data)

        output_file = basename + "_dearxiv.pdf"
        status = subprocess.call(
            [self.pdftk_path, removed_file, "output", output_file, "compress"]
        )
        if not status == 0:
            exception("pdftk failed to compress the pdf.")

        return output_file

    def run(self, src, filename=None):
        info = self.get_paper_info(src)
        clean_filename = self.create_filename(info, filename)
        tmp_filename = "paper.pdf"

        self.initial_dir = os.getcwd()
        with tempfile.TemporaryDirectory() as working_dir:
            os.chdir(working_dir)
            self.retrieve_pdf(src, tmp_filename)
            self.check_file_is_pdf(tmp_filename)

            ops = [
                self.dearxiv,
                self.crop_pdf,
                self.center_pdf,
                self.blank_pdf,
                self.shrink_pdf,
            ]
            intermediate_fname = tmp_filename
            for op in ops:
                intermediate_fname = op(intermediate_fname)
            shutil.move(intermediate_fname, clean_filename)

            if self.debug:
                print("Paused in debug mode in dir: %s" % working_dir)
                print("Press enter to exit.")
                return input()

            if self.upload:
                return self.upload_to_rm(clean_filename)

            target_path = os.path.join(self.initial_dir, clean_filename)
            while os.path.exists(target_path):
                base = os.path.splitext(target_path)[0]
                target_path = base + "_.pdf"
            shutil.move(clean_filename, target_path)
            return target_path


class ArxivProvider(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_abs_pdf_urls(self, url):
        """Get the pdf and abs url from any given arXiv url """
        if re.match("https?://arxiv.org/abs/\d{4}\.\d{4,5}(v\d+)?", url):
            abs_url = url
            pdf_url = url.replace("abs", "pdf") + ".pdf"
        elif re.match(
            "https?://arxiv.org/pdf/\d{4}\.\d{4,5}(v\d+)?\.pdf", url
        ):
            abs_url = url[:-4].replace("pdf", "abs")
            pdf_url = url
        else:
            exception("Couldn't figure out arXiv urls.")
        return abs_url, pdf_url

    def validate(src):
        """Check if the url is to an arXiv page. """
        m = re.match(
            "https?://arxiv.org/(abs|pdf)/\d{4}\.\d{4,5}(v\d+)?(\.pdf)?", src
        )
        return not m is None

    def retrieve_pdf(self, src, filename):
        """ Download the file and save as filename """
        _, pdf_url = self.get_abs_pdf_urls(src)
        self.download_url(pdf_url, filename)

    def get_paper_info(self, src):
        """ Extract the paper's authors, title, and publication year """
        abs_url, _ = self.get_abs_pdf_urls(src)
        self.log("Getting paper info from arXiv")
        page = self.get_page_with_retry(abs_url)
        soup = bs4.BeautifulSoup(page, "html.parser")
        authors = [
            x["content"]
            for x in soup.find_all("meta", {"name": "citation_author"})
        ]
        authors = [x.split(",")[0].strip() for x in authors]
        title = soup.find_all("meta", {"name": "citation_title"})[0]["content"]
        date = soup.find_all("meta", {"name": "citation_date"})[0]["content"]
        return dict(title=title, date=date, authors=authors)


class PMCProvider(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_abs_pdf_urls(self, url):
        """Get the pdf and html url from a given PMC url """
        if re.match(
            "https?://www.ncbi.nlm.nih.gov/pmc/articles/PMC\d+/pdf/nihms\d+\.pdf",
            url,
        ):
            idx = url.index("pdf")
            abs_url = url[: idx - 1]
            pdf_url = url
        elif re.match(
            "https?://www.ncbi.nlm.nih.gov/pmc/articles/PMC\d+/?", url
        ):
            abs_url = url
            pdf_url = url.rstrip("/") + "/pdf"  # it redirects, usually
        else:
            exception("Couldn't figure out PMC urls.")
        return abs_url, pdf_url

    def validate(src):
        m = re.fullmatch(
            "https?://www.ncbi.nlm.nih.gov/pmc/articles/PMC\d+.*", src
        )
        return not m is None

    def retrieve_pdf(self, src, filename):
        _, pdf_url = self.get_abs_pdf_urls(src)
        self.download_url(pdf_url, filename)

    def get_paper_info(self, src):
        """ Extract the paper's authors, title, and publication year """
        self.log("Getting paper info from PMC")
        page = self.get_page_with_retry(src)
        soup = bs4.BeautifulSoup(page, "html.parser")
        authors = [
            x["content"]
            for x in soup.find_all("meta", {"name": "citation_authors"})
        ]
        # We only use last names, and this method is a guess at best. I'm open to
        # more advanced approaches.
        authors = [
            x.strip().split(" ")[-1].strip() for x in authors[0].split(",")
        ]
        title = soup.find_all("meta", {"name": "citation_title"})[0]["content"]
        date = soup.find_all("meta", {"name": "citation_date"})[0]["content"]
        if re.match("\w+\ \d{4}", date):
            date = date.split(" ")[-1]
        else:
            date = date.replace(" ", "_")
        return dict(title=title, date=date, authors=authors)


class ACMProvider(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_acm_pdf_url(self, url):
        page = self.get_page_with_retry(url)
        soup = bs4.BeautifulSoup(page, "html.parser")
        thea = None
        for a in soup.find_all("a"):
            if a.get("name") == "FullTextPDF":
                thea = a
                break
        if thea is None:
            return None
        href = thea.get("href")
        if href.startswith("http"):
            return href
        else:
            return "https://dl.acm.org/" + href

    def get_abs_pdf_urls(self, url):
        if re.match("https?://dl.acm.org/citation.cfm\?id=\d+", url):
            abs_url = url
            pdf_url = self.get_acm_pdf_url(url)
            if pdf_url is None:
                exception(
                    "Couldn't extract PDF url from ACM citation page. Maybe it's behind a paywall?"
                )
        else:
            exception(
                "Couldn't figure out ACM urls, please provide a URL of the "
                "format: http(s)://dl.acm.org/citation.cfm?id=..."
            )
        return abs_url, pdf_url

    def retrieve_pdf(self, src, filename):
        _, pdf_url = self.get_abs_pdf_urls(src)
        self.download_url(pdf_url, filename)

    def validate(src):
        m = re.fullmatch("https?://dl.acm.org/citation.cfm\?id=\d+", src)
        return not m is None

    def get_paper_info(self, src):
        """ Extract the paper's authors, title, and publication year """
        self.log("Getting paper info from ACM")
        page = self.get_page_with_retry(src)
        soup = bs4.BeautifulSoup(page, "html.parser")
        authors = [
            x["content"]
            for x in soup.find_all("meta", {"name": "citation_authors"})
        ]
        # We only use last names, and this method is a guess. I'm open to more
        # advanced approaches.
        authors = [
            x.strip().split(",")[0].strip() for x in authors[0].split(";")
        ]
        title = soup.find_all("meta", {"name": "citation_title"})[0]["content"]
        date = soup.find_all("meta", {"name": "citation_date"})[0]["content"]
        if not re.match("\d{2}/\d{2}/\d{4}", date.strip()):
            self.warn(
                "Couldn't extract year from ACM page, please raise an "
                "issue on GitHub so I can fix it: %s" % GITHUB_URL
            )
        date = date.strip().split("/")[-1]
        return dict(title=title, date=date, authors=authors)


class LocalFileProvider(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(src):
        return os.path.exists(src)

    def retrieve_pdf(self, src, filename):
        source = os.path.join(self.initial_dir, src)
        shutil.copy(source, filename)

    def get_paper_info(self, src):
        return {"filename": src}

    def create_filename(self, info, filename=None):
        if not filename is None:
            return filename
        return os.path.basename(info["filename"])


class PdfUrlProvider(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(src):
        try:
            result = urllib.parse.urlparse(src)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False

    def retrieve_pdf(self, url, filename):
        self.download_url(url, filename)

    def get_paper_info(self, src):
        return None

    def create_filename(self, info, filename=None):
        if filename is None:
            exception(
                "Filename must be provided with PDFUrlProvider (use --filename)"
            )
        return filename


def exception(msg):
    print("ERROR: " + msg, file=sys.stderr)
    print("Error occurred. Exiting.", file=sys.stderr)
    raise SystemExit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-b",
        "--blank",
        help="Add a blank page after every page of the PDF",
        action="store_true",
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
        "-c",
        "--center",
        help="Center the PDF on the page, instead of left align",
        action="store_true",
    )
    parser.add_argument(
        "--filename",
        help="Filename to use for the file on reMarkable",
        default=None,
    )
    parser.add_argument(
        "-p",
        "--remarkable-path",
        help="directory on reMarkable to put the file (created if missing)",
        dest="remarkable_dir",
        default="/",
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


def main():
    args = parse_args()

    providers = [
        ArxivProvider,
        PMCProvider,
        ACMProvider,
        LocalFileProvider,
        PdfUrlProvider,
    ]

    provider = next((p for p in providers if p.validate(args.input)), None)
    if provider is None:
        exception("Input not valid, no provider can handle this source.")

    prov = provider(
        verbose=args.verbose,
        upload=not args.no_upload,
        debug=args.debug,
        center=args.center,
        blank=args.blank,
        remarkable_dir=args.remarkable_dir,
        rmapi_path=args.rmapi,
        pdfcrop_path=args.pdfcrop,
        pdftk_path=args.pdftk,
        gs_path=args.gs,
    )

    prov.run(args.input, filename=args.filename)


if __name__ == "__main__":
    main()
