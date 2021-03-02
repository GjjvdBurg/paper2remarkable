# -*- coding: utf-8 -*-

"""Provider for PMLR

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class PMLRInformer(Informer):

    meta_date_key = "citation_publication_date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class PMLR(Provider):

    re_abs_1 = "https?://proceedings.mlr.press/v\d+/[\w\-\w]+\d+.html"
    re_pdf_1 = "https?://proceedings.mlr.press/v\d+/[\w\-\w]+\d+.pdf"

    re_abs_2 = "https?://proceedings.mlr.press/v\d+/[\w\-\w]+\d+\w?.html"
    re_pdf_2 = "https?://proceedings.mlr.press/v\d+/(?P<ref>[\w\-\w]+\d+\w?)/(?P=ref).pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = PMLRInformer()

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract url from a OpenReview url """
        if re.match(self.re_abs_1, url):
            abs_url = url
            pdf_url = url.replace(".html", ".pdf")
        elif re.match(self.re_pdf_1, url):
            abs_url = url.replace(".pdf", ".html")
            pdf_url = url
        elif re.match(self.re_abs_2, url):
            abs_url = url
            parts = url.split("/")
            authoridx = parts[-1].split(".")[0]
            pdf_url = "/".join(parts[:-1]) + "/%s/%s.pdf" % (
                authoridx,
                authoridx,
            )
        elif re.match(self.re_pdf_2, url):
            parts = url.split("/")
            abs_url = "/".join(parts[:-1]) + ".html"
            pdf_url = url
        else:
            raise URLResolutionError("PMLR", url)
        return abs_url, pdf_url

    def validate(src):
        return (
            re.fullmatch(PMLR.re_abs_1, src)
            or re.fullmatch(PMLR.re_pdf_1, src)
            or re.fullmatch(PMLR.re_abs_2, src)
            or re.fullmatch(PMLR.re_pdf_2, src)
        )
