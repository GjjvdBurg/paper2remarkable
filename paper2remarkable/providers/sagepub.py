# -*- coding: utf-8 -*-

"""Provider for SagePub

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class SagePubInformer(Informer):

    meta_author_key = "dc.Creator"
    meta_title_key = "dc.Title"
    meta_date_key = "dc.Date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)

    def _format_year(self, soup_date):
        return soup_date.split("-")[0]


class SagePub(Provider):

    re_abs = "https?:\/\/journals\.sagepub\.com\/doi\/full\/\d{2}\.\d{4}\/\d+"
    re_pdf = "https?:\/\/journals\.sagepub\.com\/doi\/pdf\/\d{2}\.\d{4}\/\d+"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = SagePubInformer()

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.replace("full", "pdf")
        elif re.match(self.re_pdf, url):
            pdf_url = url
            abs_url = url.replace("pdf", "full")
        else:
            raise URLResolutionError("SagePub", url)
        return abs_url, pdf_url

    def validate(src):
        return re.match(SagePub.re_abs, src) or re.match(SagePub.re_pdf, src)
