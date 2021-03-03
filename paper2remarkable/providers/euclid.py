# -*- coding: utf-8 -*-

"""Provider for Project Euclid

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2021, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError, Error


class EuclidError(Error):
    """Exception raised when captcha is presented"""

    def __str__(self):
        msg = (
            "ERROR: Couldn't process URL as the site returned "
            "a challenge response (captcha). You might want to "
            "download the file and run p2r on the local file. "
            "\n"
            "This is a known issue with ProjectEuclid and is "
            "not a bug."
        )
        return msg


class EuclidInformer(Informer):

    meta_date_key = "citation_publication_date"

    def get_filename(self, abs_url, cookiejar=None):
        name = super().get_filename(abs_url, cookiejar=cookiejar)
        if name == "_-__.pdf":
            raise EuclidError()
        return name

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class Euclid(Provider):

    re_abs = "^https://projecteuclid.org/journals/[0-9a-zA-Z\-\.\/]*?.full$"
    re_pdf = "^https://projecteuclid.org/journals/[0-9a-zA-Z\-\.\/]*?.pdf$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = EuclidInformer()
        self.server_delay = 30

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract url from a OpenReview url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.replace(".full", ".pdf")
        elif re.match(self.re_pdf, url):
            abs_url = url.replace(".pdf", ".full")
            pdf_url = url
        else:
            raise URLResolutionError("Euclid", url)
        return abs_url, pdf_url

    def validate(src):
        m = re.match(Euclid.re_abs, src) or re.match(Euclid.re_pdf, src)
        return m is not None
