# -*- coding: utf-8 -*-

"""Provider for ACL

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2021, G.J.J. van den Burg

"""

import re

from ..exceptions import URLResolutionError
from ._base import Provider
from ._info import Informer


class ACLInformer(Informer):

    meta_date_key = "citation_publication_date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class ACL(Provider):

    re_abs_1 = "^https://www.aclweb.org/anthology/(?P<key>[0-9a-zA-Z\.\-]+)"
    re_abs_2 = "^https://(www.)?aclanthology.org/(?P<key>[0-9a-zA-Z\.\-]+)"
    re_pdf_1 = "^https://www.aclweb.org/anthology/(?P<key>[0-9a-zA-Z\.\-]*?)(v\d+)?.pdf"
    re_pdf_2 = "^https://(www.)?aclanthology.org/(?P<key>[0-9a-zA-Z\.\-]*?)(v\d+)?.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = ACLInformer()

    def get_abs_pdf_urls(self, url):
        m = re.match(self.re_pdf_1, url)
        if m:
            pdf_url = url
            abs_url = f"https://www.aclweb.org/anthology/{m['key']}"
            return abs_url, pdf_url

        m = re.match(self.re_pdf_2, url)
        if m:
            pdf_url = url
            abs_url = f"https://www.aclanthology.org/{m['key']}"
            return abs_url, pdf_url

        m = re.match(self.re_abs_1, url)
        if m:
            abs_url = url
            pdf_url = f"https://www.aclweb.org/anthology/{m['key']}.pdf"
            return abs_url, pdf_url

        m = re.match(self.re_abs_2, url)
        if m:
            abs_url = url
            pdf_url = f"https://www.aclanthology.org/{m['key']}.pdf"
            return abs_url, pdf_url

        raise URLResolutionError("ACL", url)

    def validate(src):
        return (
            re.match(ACL.re_pdf_1, src)
            or re.match(ACL.re_pdf_2, src)
            or re.match(ACL.re_abs_1, src)
            or re.match(ACL.re_abs_2, src)
        )
