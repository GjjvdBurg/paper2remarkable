# -*- coding: utf-8 -*-

"""Provider for JMLR

Journal of Machine Learning Research

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class JMLRInformer(Informer):

    meta_date_key = "citation_publication_date"

    def _format_authors(self, soup_authors):
        have_comma = any(("," in auth for auth in soup_authors))
        if have_comma:
            return super()._format_authors(soup_authors, sep=",", idx=0)
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class JMLR(Provider):

    re_abs_1 = "https?://(www\.)?jmlr\.org/papers/v(?P<vol>\d+)/(?P<pid>\d{2}\-\d{3}).html$"
    re_pdf_1 = "https?://(www\.)?jmlr\.org/papers/volume(?P<vol>\d+)/(?P<pid>\d{2}\-\d{3})/(?P=pid).pdf$"

    re_abs_2 = "https?://(www\.)?jmlr\.org/papers/v(?P<vol>\d+)/(?P<pid>\w+\d{2}\w).html$"
    re_pdf_2 = "https?://(www\.)?jmlr\.org/papers/volume(?P<vol>\d+)/(?P<pid>\w+\d{2}\w)/(?P=pid).pdf$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = JMLRInformer()

    def get_abs_pdf_urls(self, url):
        abs_url = pdf_url = None
        abs_fmt = "http://jmlr.org/papers/v{vol}/{pid}.html"
        pdf_fmt = "http://jmlr.org/papers/volume{vol}/{pid}/{pid}.pdf"
        formats = [
            (self.re_abs_1, self.re_pdf_1),
            (self.re_abs_2, self.re_pdf_2),
        ]

        for re_abs, re_pdf in formats:
            ma = re.match(re_abs, url)
            mp = re.match(re_pdf, url)
            if ma:
                abs_url = url
                pdf_url = pdf_fmt.format(
                    vol=ma.group("vol"), pid=ma.group("pid")
                )
            elif mp:
                abs_url = abs_fmt.format(
                    vol=mp.group("vol"), pid=mp.group("pid")
                )
                pdf_url = url
        if abs_url is None or pdf_url is None:
            raise URLResolutionError("JMLR", url)
        return abs_url, pdf_url

    def validate(src):
        return (
            re.match(JMLR.re_abs_1, src)
            or re.match(JMLR.re_abs_2, src)
            or re.match(JMLR.re_pdf_1, src)
            or re.match(JMLR.re_pdf_2, src)
        )
