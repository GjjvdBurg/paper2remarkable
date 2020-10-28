# -*- coding: utf-8 -*-

"""Provider for Nature

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class NatureInformer(Informer):

    meta_date_key = "citation_online_date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class Nature(Provider):

    re_abs = "^https://www.nature.com/articles/s[a-z0-9\-]+$"
    re_pdf = "^https://www.nature.com/articles/s[a-z0-9\-]+\.pdf$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = NatureInformer()

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url + ".pdf"
        elif re.match(self.re_pdf, url):
            pdf_url = url
            abs_url = url.replace(".pdf", "")
        else:
            raise URLResolutionError("Nature", url)
        return abs_url, pdf_url

    def validate(src):
        return re.match(Nature.re_abs, src) or re.match(Nature.re_pdf, src)
