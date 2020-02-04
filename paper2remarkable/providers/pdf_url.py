# -*- coding: utf-8 -*-

"""Provider for generic PDF url

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import urllib

from ._base import Provider
from ._info import Informer
from ..exceptions import FilenameMissingError
from ..utils import get_content_type_with_retry


class PdfUrlInformer(Informer):
    def get_filename(self, abs_url):
        # if this is called, filename must not have been provided
        raise FilenameMissingError(provider="PDFUrl")


class PdfUrl(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = PdfUrlInformer()

    def get_abs_pdf_urls(self, url):
        return (None, url)

    def validate(src):
        # first check if it is a valid url
        parsed = urllib.parse.urlparse(src)
        if not all([parsed.scheme, parsed.netloc, parsed.path]):
            return False
        # next, get the header and check the content type
        ct = get_content_type_with_retry(src)
        if ct is None:
            return False
        return ct.startswith("application/pdf")
