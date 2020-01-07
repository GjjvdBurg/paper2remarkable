# -*- coding: utf-8 -*-

"""Provider for NeurIPS

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class NeurIPSInformer(Informer):

    meta_date_key = "citation_publication_date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class NeurIPS(Provider):

    re_abs = "^https?://papers.nips.cc/paper/[\d\w\-]+$"
    re_pdf = "^https?://papers.nips.cc/paper/[\d\w\-]+.pdf$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = NeurIPSInformer()

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract url from a OpenReview url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url + ".pdf"
        elif re.match(self.re_pdf, url):
            abs_url = url.replace(".pdf", "")
            pdf_url = url
        else:
            raise URLResolutionError("NeurIPS", url)
        return abs_url, pdf_url

    def validate(src):
        return re.fullmatch(NeurIPS.re_abs, src) or re.fullmatch(
            NeurIPS.re_pdf, src
        )
