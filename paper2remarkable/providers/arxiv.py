# -*- coding: utf-8 -*-

"""Provider for arxiv.org

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ..utils import exception


class Arxiv(Provider):

    re_abs = "https?://arxiv.org/abs/\d{4}\.\d{4,5}(v\d+)?"
    re_pdf = "https?://arxiv.org/pdf/\d{4}\.\d{4,5}(v\d+)?\.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_abs_pdf_urls(self, url):
        """Get the pdf and abs url from any given arXiv url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.replace("abs", "pdf") + ".pdf"
        elif re.match(self.re_pdf, url):
            abs_url = url[:-4].replace("pdf", "abs")
            pdf_url = url
        else:
            exception("Couldn't figure out arXiv urls.")
        return abs_url, pdf_url

    def validate(src):
        """Check if the url is to an arXiv page. """
        return re.match(Arxiv.re_abs, src) or re.match(Arxiv.re_pdf, src)
