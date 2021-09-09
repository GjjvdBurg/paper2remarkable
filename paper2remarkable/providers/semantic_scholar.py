# -*- coding: utf-8 -*-

"""Provider for SemanticScholar

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import re

import bs4

from ..exceptions import URLResolutionError
from ..utils import get_content_type_with_retry
from ..utils import get_page_with_retry
from ._base import Provider
from ._info import Informer


class SemanticScholarInformer(Informer):

    meta_date_key = "citation_publication_date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class SemanticScholar(Provider):

    re_abs = (
        "https?:\/\/www.semanticscholar.org/paper/[A-Za-z0-9%\-]+/[0-9a-f]{40}"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = SemanticScholarInformer()

    def get_abs_pdf_urls(self, url):
        """Get the pdf and abstract urls from a SemanticScholar url"""
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = self._get_pdf_url(abs_url)
        else:
            raise URLResolutionError("SemanticScholar", url)
        return abs_url, pdf_url

    def _get_pdf_url(self, url):
        page = get_page_with_retry(url)
        soup = bs4.BeautifulSoup(page, "html.parser")

        # First try to get the direct url to the PDF file from the HTML
        a = soup.find(
            "a",
            {
                "data-selenium-selector": "paper-link",
                "data-heap-direct-pdf-link": "true",
            },
        )
        if a:
            return a["href"]

        # Next try to get the url from the metadata (not always a pdf)
        meta = soup.find_all("meta", {"name": "citation_pdf_url"})
        if not meta:
            raise URLResolutionError(
                "SemanticScholar", url, reason="Page has no url to PDF file"
            )
        pdf_url = meta[0]["content"]

        # Check the content type to check that the data will be a pdf
        content_type = get_content_type_with_retry(pdf_url)
        if content_type is None:
            raise URLResolutionError(
                "SemanticScholar",
                url,
                reason="Can't determine content type for pdf file",
            )
        if not content_type == "application/pdf":
            raise URLResolutionError(
                "SemanticScholar",
                url,
                reason="PDF url on SemanticScholar doesn't point to a pdf file",
            )
        return pdf_url

    def validate(src):
        return re.match(SemanticScholar.re_abs, src)
