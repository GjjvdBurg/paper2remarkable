# -*- coding: utf-8 -*-

"""Provider for ACL

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2021, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class ACLInformer(Informer):

    meta_date_key = "citation_publication_date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class ACL(Provider):

    re_abs = "^https://www.aclweb.org/anthology/(?P<key>[0-9a-zA-Z\.\-]+)"
    re_pdf = "^https://www.aclweb.org/anthology/(?P<key>[0-9a-zA-Z\.\-]*?)(v\d+)?.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = ACLInformer()

    def get_abs_pdf_urls(self, url):
        m = re.match(self.re_pdf, url)
        if m:
            pdf_url = url
            abs_url = f"https://www.aclweb.org/anthology/{m['key']}"
            return abs_url, pdf_url

        m = re.match(self.re_abs, url)
        if m:
            abs_url = url
            pdf_url = f"https://www.aclweb.org/anthology/{m['key']}.pdf"
            return abs_url, pdf_url

        raise URLResolutionError("ACL", url)

    def validate(src):
        m = re.match(ACL.re_abs, src) or re.match(ACL.re_pdf, src)
        return not m is None
