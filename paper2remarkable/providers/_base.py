# -*- coding: utf-8 -*-

"""Base for the Provider class

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import abc
import bs4
import logging
import os
import shutil
import tempfile
import titlecase
import unidecode

from ..pdf_ops import crop_pdf, center_pdf, blank_pdf, shrink_pdf
from ..utils import (
    check_file_is_pdf,
    clean_string,
    download_url,
    get_page_with_retry,
    upload_to_remarkable,
)


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
        self.upload = upload
        self.debug = debug
        self.remarkable_dir = remarkable_dir
        self.rmapi_path = rmapi_path
        self.pdfcrop_path = pdfcrop_path
        self.pdftk_path = pdftk_path
        self.gs_path = gs_path

        if not self.verbose:
            logging.disable()

        # Define the operations to run on the pdf. Providers can add others
        self.operations = [("crop", self.crop_pdf)]
        if center:
            self.operations.append(("center", self.center_pdf))

        if blank:
            self.operations.append(("blank", blank_pdf))
        self.operations.append(("shrink", self.shrink_pdf))

        logging.info("Starting %s" % type(self).__name__)

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
        download_url(pdf_url, filename)

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
        logging.info("Getting paper info")
        page = get_page_with_retry(abs_url)
        soup = bs4.BeautifulSoup(page, "html.parser")
        authors = self.get_authors(soup)
        title = self.get_title(soup)
        date = self.get_date(soup)
        return dict(title=title, date=date, authors=authors)

    def create_filename(self, info):
        """ Generate filename using the info dict or filename if provided """
        # we assume that the list of authors is surname only.
        logging.info("Generating output filename")

        if len(info["authors"]) > 3:
            author_part = info["authors"][0] + "_et_al"
        else:
            author_part = "_".join(info["authors"])
        author_part = clean_string(author_part)

        title_part = clean_string(info["title"])
        title_part = titlecase.titlecase(title_part).replace(" ", "_")

        year_part = info["date"].split("/")[0]

        name = author_part + "_-_" + title_part + "_" + year_part + ".pdf"
        name = unidecode.unidecode(name)
        logging.info("Created filename: %s" % name)
        return name

    def run(self, src, filename=None):
        info = self.get_paper_info(src)
        clean_filename = filename or self.create_filename(info)
        tmp_filename = "paper.pdf"

        self.initial_dir = os.getcwd()
        with tempfile.TemporaryDirectory(prefix="a2r_") as working_dir:
            os.chdir(working_dir)
            self.retrieve_pdf(src, tmp_filename)
            check_file_is_pdf(tmp_filename)

            intermediate_fname = tmp_filename
            for op in self.operations:
                intermediate_fname = op(intermediate_fname)
            shutil.move(intermediate_fname, clean_filename)

            if self.debug:
                print("Paused in debug mode in dir: %s" % working_dir)
                print("Press enter to exit.")
                return input()

            if self.upload:
                return upload_to_remarkable(
                    clean_filename,
                    remarkable_dir=self.remarkable_dir,
                    rmapi_path=self.rmapi_path,
                )

            target_path = os.path.join(self.initial_dir, clean_filename)
            while os.path.exists(target_path):
                base = os.path.splitext(target_path)[0]
                target_path = base + "_.pdf"
            shutil.move(clean_filename, target_path)
            return target_path
