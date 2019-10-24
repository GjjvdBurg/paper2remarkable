# -*- coding: utf-8 -*-

"""Base for the Provider class

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import PyPDF2
import abc
import bs4
import datetime
import os
import requests
import shutil
import string
import subprocess
import tempfile
import time
import titlecase
import unidecode

from ..pdf_ops import crop_pdf, center_pdf, blank_pdf, shrink_pdf
from ..utils import exception

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 "
    "Safari/537.36"
}


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
        self.remarkable_dir = remarkable_dir
        self.rmapi_path = rmapi_path
        self.pdfcrop_path = pdfcrop_path
        self.pdftk_path = pdftk_path
        self.gs_path = gs_path

        # Define the operations to run on the pdf. Providers can add others
        self.operations = [("crop", self.crop_pdf)]
        if center:
            self.operations.append(("center", self.center_pdf))
        if blank:
            self.operations.append(("blank", blank_pdf))
        self.operations.append(("shrink", self.shrink_pdf))

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

    # Wrappers for pdf operations that have additional arguments
    def crop_pdf(self, filepath):
        return crop_pdf(filepath, pdfcrop_path=self.pdfcrop_path)

    def center_pdf(self, filepath):
        return center_pdf(filepath, pdfcrop_path=self.pdfcrop_path)

    def shrink_pdf(self, filepath):
        return shrink_pdf(filepath, gs_path=self.gs_path)

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

    def string_clean(self, s):
        """ Clean a string to replace accented characters with equivalents and 
        keep only the allowed characters """
        normalized = unidecode.unidecode(s)
        allowed = string.ascii_letters + string.digits + "_ ."
        cleaned = "".join(c if c in allowed else "_" for c in normalized)
        return cleaned

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
        author_part = self.string_clean(author_part)

        title_part = self.string_clean(info["title"])
        title_part = titlecase.titlecase(title_part).replace(" ", "_")

        year_part = info["date"].split("/")[0]

        name = author_part + "_-_" + title_part + "_" + year_part + ".pdf"
        name = unidecode.unidecode(name)
        self.log("Created filename: %s" % name)
        return name

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
                self.warn("Error getting url %s. Retrying in 5 seconds" % url)
                time.sleep(5)
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

    def run(self, src, filename=None):
        info = self.get_paper_info(src)
        clean_filename = self.create_filename(info, filename)
        tmp_filename = "paper.pdf"

        self.initial_dir = os.getcwd()
        with tempfile.TemporaryDirectory(prefix="a2r_") as working_dir:
            os.chdir(working_dir)
            self.retrieve_pdf(src, tmp_filename)
            self.check_file_is_pdf(tmp_filename)

            intermediate_fname = tmp_filename
            for op in self.operations:
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
