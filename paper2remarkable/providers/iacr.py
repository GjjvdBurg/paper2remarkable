# -*- coding: utf-8 -*-

"""Provider for IACR's eprints

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import os
import re
import urllib.parse

import bs4

from ..exceptions import URLResolutionError
from ..log import Logger
from ..utils import get_page_with_retry
from ._base import Provider
from ._info import Informer

logger = Logger()


class IACRInformer(Informer):
    def get_title(self, soup):
        title = soup.find_all("title")
        if not title:
            logger.warning(
                "Couldn't determine title information, maybe provide the desired filename using '--filename'?"
            )
            return ""
        return title[0].get_text().split("-", maxsplit=1)[-1]

    def get_authors(self, soup):
        i = soup.find_all("i")
        if not i:
            logger.warning(
                "Couldn't determine author information, maybe provide the desired filename using '--filename'?"
            )
            return ""
        authors = i[0].get_text()
        authors = authors.replace("  ", " ")
        authors = authors.split(" and ")
        return self._format_authors(authors, sep=" ", idx=-1)

    def get_year(self, soup):
        h2 = soup.find_all("h2")
        if not h2:
            logger.warning(
                "Couldn't determine year information, maybe provide the desired filename using '--filename'?"
            )
            return ""
        text = h2[0].get_text()
        report = text.split(":", maxsplit=1)[-1]
        year_num = report.strip().split(" ")[1]
        year = year_num.split("/")[0]
        return year


class IACR(Provider):

    re_abs = "https?://eprint.iacr.org/\d{4}/\d+$"
    re_pdf = "https?://eprint.iacr.org/\d{4}/\d+\.pdf$"
    re_ps = "https?://eprint.iacr.org/\d{4}/\d+\.ps$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = IACRInformer()

    def _get_doc_url(self, abs_url):
        page = get_page_with_retry(abs_url)
        soup = bs4.BeautifulSoup(page, "html.parser")

        bb = soup.find_all("b")
        b = next((b for b in bb if "Available format" in b.get_text()), None)
        if b is None:
            # Fallback
            return abs_url + ".pdf"
        aa = b.find_next_siblings("a")
        a = next((a for a in aa if "PDF" in a.get_text()), None)
        if not a is None:
            return urllib.parse.urljoin(abs_url, a.get("href"))
        a = next((a for a in aa if "Postscript (PS)" in a.get_text()), None)
        if not a is None:
            return urllib.parse.urljoin(abs_url, a.get("href"))
        # Fallback
        return abs_url + ".pdf"

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = self._get_doc_url(url)
        elif re.match(self.re_pdf, url):
            abs_url = url[: -len(".pdf")]
            pdf_url = url
        elif re.match(self.re_ps, url):
            abs_url = url[: -len(".ps")]
            pdf_url = url
        else:
            raise URLResolutionError("IACR", url)
        return abs_url, pdf_url

    def retrieve_pdf(self, pdf_url, filename):
        # Bit hacky, can consider adding first-class PS support
        tmpfilename = os.path.splitext(filename)[0] + "-tmp.pdf"
        super().retrieve_pdf(pdf_url, tmpfilename)
        self.rewrite_pdf(tmpfilename, out_pdf=filename)

    def validate(src):
        return re.match(IACR.re_abs, src) or re.match(IACR.re_pdf, src)
