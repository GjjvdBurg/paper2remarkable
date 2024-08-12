# -*- coding: utf-8 -*-

"""Provider for PubMed

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re

from ..exceptions import URLResolutionError
from ._base import Provider
from ._info import Informer


class PubMedInformer(Informer):
    meta_date_key = "citation_publication_date"
    meta_author_key = "citation_author"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class PubMed(Provider):
    re_abs = r"https?://www.ncbi.nlm.nih.gov/pmc/articles/PMC\d+/?"
    re_pdf = (
        r"https?://www.ncbi.nlm.nih.gov/pmc/articles/PMC\d+/pdf/nihms\d+\.pdf"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = PubMedInformer()

    def get_abs_pdf_urls(self, url):
        """Get the pdf and html url from a given PMC url"""
        if re.match(self.re_pdf, url):
            idx = url.index("pdf")
            abs_url = url[: idx - 1]
            pdf_url = url
        elif re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.rstrip("/") + "/pdf"  # it redirects, usually
        else:
            raise URLResolutionError("PMC", url)
        return abs_url, pdf_url

    @staticmethod
    def validate(src):
        return re.match(PubMed.re_abs, src) or re.match(PubMed.re_pdf, src)
