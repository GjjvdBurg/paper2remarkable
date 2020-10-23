# -*- coding: utf-8 -*-

"""Provider for CVF

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer

from ..exceptions import URLResolutionError
from ..log import Logger

logger = Logger()


class CVFInformer(Informer):

    meta_date_key = "citation_publication_date"


class CVF(Provider):

    re_abs = "^https?://openaccess.thecvf.com/content_([\w\d]+)/html/([\w\d\_\-]+).html$"
    re_pdf = "^https?://openaccess.thecvf.com/content_([\w\d]+)/papers/([\w\d\_\-]+).pdf$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = CVFInformer()

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url[: -len(".html")]
            pdf_url += ".pdf"
            pdf_url = pdf_url.replace("html", "papers")
        elif re.match(self.re_pdf, url):
            pdf_url = url
            abs_url = url.replace("papers", "html").replace(".pdf", ".html")
        else:
            raise URLResolutionError("CVF", url)
        return abs_url, pdf_url

    def validate(src):
        m = re.match(CVF.re_abs, src) or re.match(CVF.re_pdf, src)
        return not m is None
