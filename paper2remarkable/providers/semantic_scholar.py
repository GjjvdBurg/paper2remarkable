# -*- coding: utf-8 -*-

"""Provider for SemanticScholar

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import re
import bs4

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError
from ..utils import get_page_with_retry


class SemanticScholarInformer(Informer):

    meta_date_key = "citation_publication_date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class SemanticScholar(Provider):

    re_abs = (
        "https?:\/\/www.semanticscholar.org/paper/[A-Za-z0-9%\-]+/[0-9a-f]{40}"
    )
    re_pdf = "https?:\/\/pdfs.semanticscholar.org/[0-9a-f]{4}/[0-9a-f]{36}.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = SemanticScholarInformer()

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract urls from a SemanticScholar url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = self._get_pdf_url(abs_url)
        elif re.match(self.re_pdf, url):
            pdf_url = url
            remainder = pdf_url.split("/")[-1][: -len(".pdf")]
            first_four = pdf_url.split("/")[-2]
            paper_id = first_four + remainder
            abs_url = f"https://www.semanticscholar.org/paper/{paper_id}"
        else:
            raise URLResolutionError("SemanticScholar", url)
        return abs_url, pdf_url

    def _get_pdf_url(self, url):
        page = get_page_with_retry(url)
        soup = bs4.BeautifulSoup(page, "html.parser")
        meta = soup.find_all("meta", {"name": "citation_pdf_url"})
        if not meta:
            raise URLResolutionError("SemanticScholar", url)
        return meta[0]["content"]

    def validate(src):
        return re.match(SemanticScholar.re_abs, src) or re.match(
            SemanticScholar.re_pdf, src
        )
