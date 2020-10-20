# -*- coding: utf-8 -*-

"""Provider for NBER

(US) National Bureau of Economic Research

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class NBERInformer(Informer):

    meta_date_key = "citation_publication_date"

    def _format_authors(self, soup_authors, sep=" ", idx=0, op=None):
        return super()._format_authors(soup_authors, sep=" ", idx=-1, op=None)


class NBER(Provider):

    re_abs = "https?://www\.nber\.org/papers/(?P<ref>[a-z0-9]+)$"
    re_pdf = "https?://www\.nber\.org/papers/(?P<ref>[a-z0-9]+)\.pdf$"

    re_pdf_2 = "https://www.nber.org/system/files/working_papers/(?P<ref>[a-z0-9]+)/(?P=ref).pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = NBERInformer()

    def get_report_no(self, url):
        m = re.match(self.re_pdf_2, url)
        if m:
            return m["ref"]
        raise URLResolutionError(
            "NBER", url, reason="Failed to retrieve report number."
        )

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url + ".pdf"
        elif re.match(self.re_pdf, url):
            pdf_url = url
            abs_url = url[: -len(".pdf")]
        elif re.match(self.re_pdf_2, url):
            ref = self.get_report_no(url)
            abs_url = f"https://www.nber.org/papers/{ref}"
            pdf_url = url
        else:
            raise URLResolutionError("NBER", url)
        return abs_url, pdf_url

    def validate(src):
        return (
            re.match(NBER.re_abs, src)
            or re.match(NBER.re_pdf, src)
            or re.match(NBER.re_pdf_2, src)
        )
