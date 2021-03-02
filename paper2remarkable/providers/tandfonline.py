# -*- coding: utf-8 -*-

"""Provider for Taylor and Francis Online

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError
from ..log import Logger

logger = Logger()


class TandFOnlineInformer(Informer):
    meta_title_key = "dc.Title"
    meta_author_key = "dc.Creator"
    meta_date_key = "dc.Date"

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)

    def _format_year(self, soup_date):
        return soup_date.strip().split(" ")[-1].strip()


class TandFOnline(Provider):

    re_abs = "^https?://\w+.tandfonline.com/doi/(full|abs)/(?P<doi>\d+\.\d+/\d+\.\d+\.\d+)"
    re_pdf = "^https?://\w+.tandfonline.com/doi/(full|pdf)/(?P<doi>\d+\.\d+/\d+\.\d+\.\d+)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = TandFOnlineInformer()

    def _get_doi(self, url):
        m = re.match(self.re_abs, url) or re.match(self.re_pdf, url)
        if m:
            return m["doi"]
        raise URLResolutionError(
            "TandFOnline", url, reason="Failed to retrieve DOI."
        )

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            doi = self._get_doi(url)
            pdf_url = "https://www.tandfonline.com/doi/pdf/{doi}?needAccess=true".format(
                doi=doi
            )
        elif re.match(self.re_pdf, url):
            doi = self._get_doi(url)
            pdf_url = "https://www.tandfonline.com/doi/pdf/{doi}?needAccess=true".format(
                doi=doi
            )
            # full redirects to abs if we don't have access
            abs_url = "https://www.tandfonline.com/doi/full/{doi}".format(
                doi=doi
            )
        else:
            raise URLResolutionError("TandFOnline", url)
        return abs_url, pdf_url

    def validate(src):
        m = re.match(TandFOnline.re_abs, src) or re.match(
            TandFOnline.re_pdf, src
        )
        return not m is None
