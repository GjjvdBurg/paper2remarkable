# -*- coding: utf-8 -*-

"""Provider for generic PDF url

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import urllib

from ._base import Provider
from ._info import Informer

from .. import GITHUB_URL
from ..exceptions import FilenameMissingError
from ..log import Logger
from ..utils import get_content_type_with_retry

logger = Logger()


class PdfUrlInformer(Informer):
    def get_filename(self, abs_url):
        # try to get a nice filename by parsing the url
        parsed = urllib.parse.urlparse(abs_url)
        path_parts = parsed.path.split("/")
        if not path_parts:
            raise FilenameMissingError(
                provider="PdfUrl",
                url=abs_url,
                reason="No URL parts",
            )

        filename = path_parts[-1]
        if not filename.endswith(".pdf"):
            raise FilenameMissingError(
                provider="PdfUrl",
                url=abs_url,
                reason="URL path didn't end in .pdf",
            )
        logger.warning(
            "Using filename {filename} extracted from url. "
            "You might want to provide a nicer one using --filename "
            "or request this paper source to be added "
            "(see: {github}).".format(filename=filename, github=GITHUB_URL)
        )
        return filename


class PdfUrl(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = PdfUrlInformer()

    def get_abs_pdf_urls(self, url):
        return (url, url)

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
