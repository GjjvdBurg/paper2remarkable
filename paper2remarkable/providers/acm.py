# -*- coding: utf-8 -*-

"""Provider for ACM

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import bs4
import re

from ._base import Provider
from ._info import Informer
from .. import GITHUB_URL
from ..utils import exception, get_page_with_retry
from ..log import Logger

logger = Logger()


class ACMInformer(Informer):
    meta_author_key = "citation_authors"

    def _format_authors(self, soup_authors):
        op = lambda x: x[0].split(";")
        return super()._format_authors(soup_authors, sep=",", idx=0, op=op)

    def _format_year(self, soup_date):
        if not re.match("\d{2}/\d{2}/\d{4}", soup_date.strip()):
            logger.warning(
                "Couldn't extract year from ACM page, please raise an "
                "issue on GitHub so it can be fixed: %s" % GITHUB_URL
            )
        return soup_date.strip().split("/")[-1]


class ACM(Provider):

    re_abs = "https?://dl.acm.org/citation.cfm\?id=\d+"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = ACMInformer()

    def get_acm_pdf_url(self, url):
        page = get_page_with_retry(url)
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
