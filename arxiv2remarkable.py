#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.3.1"
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
import pdfplumber
import re
import requests
import shutil
import subprocess
import sys
import tempfile
import time
import titlecase
import unidecode
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

    meta_author_key = "citation_author"
    meta_title_key = "citation_title"
    meta_date_key = "citation_date"

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

    def retrieve_pdf(self, src, filename):
        """ Download pdf from src and save to filename """
        _, pdf_url = self.get_abs_pdf_urls(src)
        self.download_url(pdf_url, filename)

    def _format_authors(self, soup_authors, sep=",", idx=0, op=None):
        op = (lambda x: x) if op is None else op
        # format the author list retrieved by bs4
        return [x.strip().split(sep)[idx].strip() for x in op(soup_authors)]

    def get_authors(self, soup):
        authors = [
            x["content"]
            for x in soup.find_all("meta", {"name": self.meta_author_key})
        ]
        return self._format_authors(authors)

    def get_title(self, soup):
        target = soup.find_all("meta", {"name": self.meta_title_key})
        return target[0]["content"]

    def _format_date(self, soup_date):
        return soup_date

    def get_date(self, soup):
        date = soup.find_all("meta", {"name": self.meta_date_key})[0][
            "content"
        ]
        return self._format_date(date)

    def get_paper_info(
        self,
        src,
        author_key="citation_author",
        title_key="citation_title",
        date_key="citation_date",
    ):
        """ Retrieve the title/author (surnames)/year information """
        abs_url, _ = self.get_abs_pdf_urls(src)
        self.log("Getting paper info")
        page = self.get_page_with_retry(abs_url)
        soup = bs4.BeautifulSoup(page, "html.parser")
        authors = self.get_authors(soup)
        title = self.get_title(soup)
        date = self.get_date(soup)
        return dict(title=title, date=date, authors=authors)

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
        name = unidecode.unidecode(name)
        self.log("Created filename: %s" % name)
        return name

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
        cropped_file = os.path.splitext(filepath)[0] + "-crop.pdf"
        cropper = Cropper(
            filepath, cropped_file, pdfcrop_path=self.pdfcrop_path
        )
        status = cropper.crop(margins=15)

        if not status == 0:
            self.warn("Failed to crop the pdf file at: %s" % filepath)
            return filepath
        if not os.path.exists(cropped_file):
            self.warn(
                "Can't find cropped file '%s' where expected." % cropped_file
            )
            return filepath
        return cropped_file

    def center_pdf(self, filepath):
        if not self.center:
            return filepath

        self.log("Centering pdf file")
        centered_file = os.path.splitext(filepath)[0] + "-center.pdf"
        cropper = Cropper(
            filepath, centered_file, pdfcrop_path=self.pdfcrop_path
        )
        status = cropper.center()
        if not status == 0:
            self.warn("Failed to center the pdf file at: %s" % filepath)
            return filepath
        if not os.path.exists(centered_file):
            self.warn(
                "Can't find centered file '%s' where expected." % centered_file
            )
            return filepath
        return centered_file

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
                [self.rmapi_path, "mkdir", remarkable_dir + "/"],
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
        with tempfile.TemporaryDirectory(prefix="a2r_") as working_dir:
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


class Arxiv(Provider):

    re_abs = "https?://arxiv.org/abs/\d{4}\.\d{4,5}(v\d+)?"
    re_pdf = "https?://arxiv.org/pdf/\d{4}\.\d{4,5}(v\d+)?\.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_abs_pdf_urls(self, url):
        """Get the pdf and abs url from any given arXiv url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.replace("abs", "pdf") + ".pdf"
        elif re.match(self.re_pdf, url):
            abs_url = url[:-4].replace("pdf", "abs")
            pdf_url = url
        else:
            exception("Couldn't figure out arXiv urls.")
        return abs_url, pdf_url

    def validate(src):
        """Check if the url is to an arXiv page. """
        return re.match(Arxiv.re_abs, src) or re.match(Arxiv.re_pdf, src)


class Pubmed(Provider):

    meta_author_key = "citation_authors"

    re_abs = "https?://www.ncbi.nlm.nih.gov/pmc/articles/PMC\d+/?"
    re_pdf = (
        "https?://www.ncbi.nlm.nih.gov/pmc/articles/PMC\d+/pdf/nihms\d+\.pdf"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_abs_pdf_urls(self, url):
        """Get the pdf and html url from a given PMC url """
        if re.match(self.re_pdf, url):
            idx = url.index("pdf")
            abs_url = url[: idx - 1]
            pdf_url = url
        elif re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.rstrip("/") + "/pdf"  # it redirects, usually
        else:
            exception("Couldn't figure out PMC urls.")
        return abs_url, pdf_url

    def validate(src):
        return re.match(Pubmed.re_abs, src) or re.match(Pubmed.re_pdf, src)

    def _format_authors(self, soup_authors):
        op = lambda x: x[0].split(",")
        return super()._format_authors(soup_authors, sep=" ", idx=-1, op=op)

    def _format_date(self, soup_date):
        if re.match("\w+\ \d{4}", soup_date):
            return soup_date.split(" ")[-1]
        return soup_date.replace(" ", "_")


class ACM(Provider):

    meta_author_key = "citation_authors"

    re_abs = "https?://dl.acm.org/citation.cfm\?id=\d+"

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
        if re.match(self.re_abs, url):
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

    def validate(src):
        m = re.fullmatch(ACM.re_abs, src)
        return not m is None

    def _format_authors(self, soup_authors):
        op = lambda x: x[0].split(";")
        return super()._format_authors(soup_authors, sep=",", idx=0, op=op)

    def _format_date(self, soup_date):
        if not re.match("\d{2}/\d{2}/\d{4}", soup_date.strip()):
            self.warn(
                "Couldn't extract year from ACM page, please raise an "
                "issue on GitHub so it can be fixed: %s" % GITHUB_URL
            )
        return soup_date.strip().split("/")[-1]


class OpenReview(Provider):

    meta_date_key = "citation_publication_date"

    re_abs = "https?://openreview.net/forum\?id=[A-Za-z0-9]+"
    re_pdf = "https?://openreview.net/pdf\?id=[A-Za-z0-9]+"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract url from a OpenReview url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.replace("forum", "pdf")
        elif re.match(self.re_pdf, url):
            abs_url = url.replace("pdf", "forum")
            pdf_url = url
        else:
            exception("Couldn't figure out OpenReview urls.")
        return abs_url, pdf_url

    def validate(src):
        """ Check if the url is a valid OpenReview url. """
        return re.match(OpenReview.re_abs, src) or re.match(
            OpenReview.re_pdf, src
        )

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class Springer(Provider):

    meta_date_key = "citation_online_date"

    re_abs = "https?:\/\/link.springer.com\/article\/10\.\d{4}\/[a-z0-9\-]+"
    re_pdf = "https?:\/\/link\.springer\.com\/content\/pdf\/10\.\d{4}(%2F|\/)[a-z0-9\-]+\.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract urls from a Springer url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.replace("article", "content/pdf")
        elif re.match(self.re_pdf, url):
            abs_url = url.replace("content/pdf", "article")
            pdf_url = url
        else:
            exception("Couldn't figure out Springer urls.")
        return abs_url, pdf_url

    def validate(src):
        return re.match(Springer.re_abs, src) or re.match(Springer.re_pdf, src)

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class LocalFile(Provider):
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


class PdfUrl(Provider):
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


class Cropper(object):
    def __init__(
        self, input_file=None, output_file=None, pdfcrop_path="pdfcrop"
    ):
        if not input_file is None:
            self.input_file = os.path.abspath(input_file)
            self.reader = PyPDF2.PdfFileReader(self.input_file)
        if not output_file is None:
            self.output_file = os.path.abspath(output_file)
        self.pdfcrop_path = pdfcrop_path

        self.writer = PyPDF2.PdfFileWriter()

    def crop(self, margins=1):
        return self.process_file(self.crop_page, margins=margins)

    def center(self, padding=15):
        return self.process_file(self.center_page, padding=padding)

    def process_file(self, page_func, *args, **kwargs):
        for page_idx in range(self.reader.getNumPages()):
            status = page_func(page_idx, *args, **kwargs)
            if not status == 0:
                return status
        with open(self.output_file, "wb") as fp:
            self.writer.write(fp)
        return 0

    def center_page(self, page_idx, padding):
        return self.process_page(
            page_idx, self.get_center_bbox, padding=padding
        )

    def crop_page(self, page_idx, margins):
        return self.process_page(page_idx, self.get_bbox, margins=margins)

    def export_page(self, page_idx):
        """Helper function that exports a single page given by index """
        page = self.reader.getPage(page_idx)
        writer = PyPDF2.PdfFileWriter()
        writer.addPage(page)
        tmpfname = "./page.pdf"
        with open(tmpfname, "wb") as fp:
            writer.write(fp)
        return tmpfname

    def process_page(self, page_idx, bbox_func, *args, **kwargs):
        """Process a single page and add it to the writer """
        tmpfname = self.export_page(page_idx)
        tmpfout = "./output.pdf"
        bbox = bbox_func(tmpfname, *args, **kwargs)
        status = subprocess.call(
            [
                self.pdfcrop_path,
                "--bbox",
                " ".join(map(str, bbox)),
                tmpfname,
                tmpfout,
            ],
            stdout=subprocess.DEVNULL,
        )
        if not status == 0:
            return status
        reader = PyPDF2.PdfFileReader(tmpfout)
        page = reader.getPage(0)
        self.writer.addPage(page)
        os.unlink(tmpfname)
        os.unlink(tmpfout)
        return 0

    def get_bbox(self, filename, margins=1, resolution=72):
        """Get the bounding box, with optional margins

        if margins is integer, used for all margins, else
        margins = [left, top, right, bottom]

        We get the bounding box by finding the smallest rectangle that is 
        completely surrounded by white pixels.
        """
        if isinstance(margins, int):
            margins = [margins for _ in range(4)]
        pdf = pdfplumber.open(filename)
        im = pdf.pages[0].to_image(resolution=resolution)
        pdf.close()

        pixels = list(im.original.getdata())
        W, H = im.original.size

        # M is a list of H lists with each W integers that equal the sum of the
        # pixel values
        M = [[sum(x) for x in pixels[i * W : (i + 1) * W]] for i in range(H)]

        left, top, bottom, right = 0, 0, 0, 0
        while top < H and sum(M[top]) == W * 255 * 3:
            top += 1
        while bottom < H and sum(M[H - 1 - bottom]) == W * 255 * 3:
            bottom += 1

        # Transpose M
        M = list(zip(*M))
        while left < W and sum(M[left]) == H * 255 * 3:
            left += 1
        while right < W and sum(M[W - 1 - right]) == H * 255 * 3:
            right += 1

        left -= margins[0]
        top -= margins[1]
        right -= margins[2]
        bottom -= margins[3]

        # This is the bounding box in PIL format: (0, 0) top left
        x0, y0, x1, y1 = left, top, W - right, H - bottom

        # Get the bbox in Ghostscript format: (0, 0) bottom left
        a0, b0, a1, b1 = x0, H - y1, x1, H - y0
        return [a0, b0, a1, b1]

    def get_center_bbox(self, filename, padding=15):
        """Compute a bounding box that will center the page file on the 
        reMarkable
        """
        bbox = self.get_bbox(filename, margins=0)

        h = bbox[3] - bbox[1]
        w = bbox[2] - bbox[0]

        # we want some minimal padding all around, because it is visually more
        # pleasing.
        h_prime = h + 2 * padding
        w_prime = w + 2 * padding

        # if the document is wider than the remarkable, we add top-padding to
        # center it, otherwise we add left-padding
        x, y = 0, 0
        if h_prime / w_prime < RM_HEIGHT / RM_WIDTH:
            y = ((RM_HEIGHT / RM_WIDTH) * w_prime - h_prime) / 2
        else:
            x = ((RM_WIDTH / RM_HEIGHT) * h_prime - w_prime) / 2

        margins = [padding + x, padding + y, padding, padding]
        return self.get_bbox(filename, margins=margins)


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

    providers = [Arxiv, Pubmed, ACM, OpenReview, Springer, LocalFile, PdfUrl]

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
