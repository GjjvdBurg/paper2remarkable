# -*- coding: utf-8 -*-

"""Provider for Project Euclid

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class EuclidInformer(Informer):

    raise NotImplementedError


class ProjectEuclid(Provider):

    re_abs = "https?://projecteuclid.org/euclid\.\w+/\d+"
    re_pdf = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = EuclidInformer()

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract url from a OpenReview url """
        if re.match(self.re_abs_1, url):
            abs_url = url
            pdf_url = url.replace(".html", ".pdf")
        elif re.match(self.re_pdf_1, url):
            abs_url = url.replace(".pdf", ".html")
            pdf_url = url
        else:
            raise URLResolutionError("OpenReview", url)
        return abs_url, pdf_url

    def validate(src):
        return re.fullmatch(ProjectEuclid.re_abs, src) or re.fullmatch(
            ProjectEuclid.re_pdf, src
        )
