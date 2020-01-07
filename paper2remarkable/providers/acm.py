# -*- coding: utf-8 -*-

"""Provider for ACM

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError
from ..log import Logger

logger = Logger()


class ACMInformer(Informer):
    meta_author_key = "citation_authors"

    def get_title(self, soup):
        target = soup.find("h1", {"class": "citation__title"})
        return target.text

    def get_authors(self, soup):
        authors = [
            span.find("a").text
            for span in soup.find_all("span", {"class": "auth-name"})
        ]
        return self._format_authors(authors)

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)

    def get_year(self, soup):
        date = soup.find("span", {"class": "epub-section__date"})
        return self._format_year(date.text)

    def _format_year(self, soup_date):
        return soup_date.strip().split(" ")[-1].strip()


class ACM(Provider):

    re_abs = "^https?://dl.acm.org/doi/(?P<doi>\d+\.\d+/\d+\.\d+)"
    re_pdf = "^https?://dl.acm.org/doi/pdf/(?P<doi>\d+\.\d+/\d+\.\d+)\?download=true"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = ACMInformer()

    def _get_doi(self, url):
        m = re.match(self.re_abs, url) or re.match(self.re_pdf, url)
        if m:
            return m["doi"]
        raise URLResolutionError("ACM", url, reason="Failed to retrieve DOI.")

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            doi = self._get_doi(url)
            pdf_url = "https://dl.acm.org/doi/pdf/{doi}?download=true".format(
                doi=doi
            )
        elif re.match(self.re_pdf, url):
            pdf_url = url
            doi = self._get_doi(url)
            abs_url = "https://dl.acm.org/doi/{doi}".format(doi=doi)
        else:
            raise URLResolutionError("ACM", url)
        return abs_url, pdf_url

    def validate(src):
        m = re.match(ACM.re_abs, src) or re.match(ACM.re_pdf, src)
        return not m is None
