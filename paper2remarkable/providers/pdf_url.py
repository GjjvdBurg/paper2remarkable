# -*- coding: utf-8 -*-

"""Provider for generic PDF url

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import urllib

from . import Provider
from ..utils import exception


class PdfUrl(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(src):
        try:
            result = urllib.parse.urlparse(src)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False

    def retrieve_pdf(self, url, filename):
        self.download_url(url, filename)

    def get_paper_info(self, src):
        return None

    def create_filename(self, info, filename=None):
        if filename is None:
            exception(
                "Filename must be provided with PDFUrlProvider (use --filename)"
            )
        return filename
