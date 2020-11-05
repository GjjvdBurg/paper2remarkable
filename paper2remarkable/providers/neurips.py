# -*- coding: utf-8 -*-

"""Provider for NeurIPS

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class NeurIPSInformer(Informer):

    meta_date_key = "citation_publication_date"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_site = False

    def _format_authors(self, soup_authors):
        if self.new_site:
            return super()._format_authors(soup_authors, sep=",", idx=0)
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class NeurIPS(Provider):

    re_abs = "^https?://papers.n(eur)?ips.cc/paper/[\d\w\-]+$"
    re_pdf = "^https?://papers.n(eur)?ips.cc/paper/[\d\w\-]+.pdf$"

    re_abs_2 = "https://papers.n(eur)?ips.cc/paper/\d{4}/hash/[0-9a-f]{32}-Abstract.html"
    re_pdf_2 = (
        "https://papers.n(eur)?ips.cc/paper/\d{4}/file/[0-9a-f]{32}-Paper.pdf"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = NeurIPSInformer()

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract url from a OpenReview url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url + ".pdf"
        elif re.match(self.re_pdf, url):
            abs_url = url.replace(".pdf", "")
            pdf_url = url
        elif re.match(self.re_abs_2, url):
            self.informer.new_site = True
            abs_url = url
            pdf_url = (
                url.replace("hash", "file")
                .replace("Abstract", "Paper")
                .replace(".html", ".pdf")
            )
        elif re.match(self.re_pdf_2, url):
            self.informer.new_site = True
            pdf_url = url
            abs_url = (
                url.replace("file", "hash")
                .replace("Paper", "Abstract")
                .replace(".pdf", ".html")
            )
        else:
            raise URLResolutionError("NeurIPS", url)
        return abs_url, pdf_url

    def validate(src):
        return (
            re.fullmatch(NeurIPS.re_abs, src)
            or re.fullmatch(NeurIPS.re_pdf, src)
            or re.fullmatch(NeurIPS.re_abs_2, src)
            or re.fullmatch(NeurIPS.re_pdf_2, src)
        )
