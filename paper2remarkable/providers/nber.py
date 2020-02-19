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
    def _format_year(self, soup_date):
        return soup_date.split("-")[0]


class NBER(Provider):

    re_abs = "https?://www\.nber\.org/papers/(?P<ref>[a-z0-9]+)$"
    re_pdf = "https?://www\.nber\.org/papers/(?P<ref>[a-z0-9]+)\.pdf$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = NBERInformer()

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url + ".pdf"
        elif re.match(self.re_pdf, url):
            pdf_url = url
            abs_url = url[: -len(".pdf")]
        else:
            raise URLResolutionError("NBER", url)
        return abs_url, pdf_url

    def validate(src):
        return re.match(NBER.re_abs, src) or re.match(NBER.re_pdf, src)
