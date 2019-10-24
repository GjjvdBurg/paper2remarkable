# -*- coding: utf-8 -*-

"""Provider for generic PDF url

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import urllib

from ._base import Provider
from ._info import Informer
from ..utils import exception


class PdfUrlInformer(Informer):
    def get_filename(self, abs_url):
        # if this is called, filename must not be provided
        exception(
            "Filename must be provided with PDFUrlProvider (use --filename)"
        )


class PdfUrl(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = PdfUrlInformer()

    def get_abs_pdf_urls(self, url):
        return (None, url)

    def validate(src):
        try:
            result = urllib.parse.urlparse(src)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False
