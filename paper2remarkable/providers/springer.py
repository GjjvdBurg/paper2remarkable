# -*- coding: utf-8 -*-

"""Provider for Springer

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re
import urllib

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class SpringerInformer(Informer):

    meta_date_key = "citation_online_date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class Springer(Provider):

    re_abs = "https?:\/\/link.springer.com\/article\/10\.\d{4}\/[a-z0-9\-]+"
    re_pdf = "https?:\/\/link\.springer\.com\/content\/pdf\/10\.\d{4}(%2F|\/)[a-z0-9\-]+\.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = SpringerInformer()

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract urls from a Springer url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.replace("article", "content/pdf")
        elif re.match(self.re_pdf, url):
            abs_url = url.replace("content/pdf", "article")[: -len(".pdf")]
            pdf_url = urllib.parse.unquote(url)
        else:
            raise URLResolutionError("Springer", url)
        return abs_url, pdf_url

    def validate(src):
        return re.match(Springer.re_abs, src) or re.match(Springer.re_pdf, src)
