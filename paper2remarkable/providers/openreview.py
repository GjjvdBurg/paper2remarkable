# -*- coding: utf-8 -*-

"""Provider for OpenReview

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError


class OpenReviewInformer(Informer):

    meta_date_key = "citation_publication_date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)


class OpenReview(Provider):

    re_abs = "https?://openreview.net/forum\?id=[A-Za-z0-9]+"
    re_pdf = "https?://openreview.net/pdf\?id=[A-Za-z0-9]+"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = OpenReviewInformer()

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract url from a OpenReview url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.replace("forum", "pdf")
        elif re.match(self.re_pdf, url):
            abs_url = url.replace("pdf", "forum")
            pdf_url = url
        else:
            raise URLResolutionError("OpenReview", url)
        return abs_url, pdf_url

    def validate(src):
        """ Check if the url is a valid OpenReview url. """
        return re.match(OpenReview.re_abs, src) or re.match(
            OpenReview.re_pdf, src
        )
