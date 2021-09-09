# -*- coding: utf-8 -*-

"""Provider for Electronic Colloquium on Computational Complexity

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2021, G.J.J. van den Burg

"""

import re

import bs4

from ..exceptions import URLResolutionError
from ..log import Logger
from ._base import Provider
from ._info import Informer

logger = Logger()


class ECCCInformer(Informer):
    def _get_paper_div(self, soup):
        h3 = soup.find(lambda t: t.name == "h3" and t.get_text() == "Paper:")
        div = h3.find_next_sibling("div")
        return bs4.BeautifulSoup(div.prettify(), "html.parser")

    def get_title(self, soup):
        divsoup = self._get_paper_div(soup)
        h4 = divsoup.find("h4")
        if not h4:
            logger.warning(
                "Couldn't determine title information, maybe provide the desired filename using '--filename'?"
            )
            return ""
        return h4.get_text().strip()

    def get_authors(self, soup):
        divsoup = self._get_paper_div(soup)
        aa = divsoup.find_all(
            lambda t: t.name == "a" and t.get("href").startswith("/author/")
        )
        if not aa:
            logger.warning(
                "Couldn't determine author information, maybe provide the desired filename using '--filename'?"
            )
            return ""
        authors = [a.get_text() for a in aa]
        return self._format_authors(authors, sep=" ", idx=-1)

    def get_year(self, soup):
        divsoup = self._get_paper_div(soup)
        line = next(
            (l for l in divsoup.text.split("\n") if "Publication: " in l), None
        )
        if line is None:
            logger.warning(
                "Couldn't determine year information, maybe provide the desired filename using '--filename'?"
            )
            return ""
        year = line.strip().split(" ")[3]  # bit lazy
        return year


class ECCC(Provider):

    re_abs = "https?://eccc.weizmann.ac.il/report/\d{4}/\d+/?$"
    re_pdf = "https?://eccc.weizmann.ac.il/report/\d{4}/\d+/download/?$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = ECCCInformer()

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.rstrip("/") + "/download"
        elif re.match(self.re_pdf, url):
            abs_url = url.rstrip("/")[: -len("/download")]
            pdf_url = url
        else:
            raise URLResolutionError("ECCC", url)
        return abs_url, pdf_url

    def validate(src):
        return re.match(ECCC.re_abs, src) or re.match(ECCC.re_pdf, src)
