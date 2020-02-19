# -*- coding: utf-8 -*-

"""Provider for CiteSeerX

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re
import time

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError
from ..log import Logger

logger = Logger()


class CiteSeerXInformer(Informer):

    meta_author_key = "citation_authors"
    meta_date_key = "citation_year"

    def _format_authors(self, soup_authors):
        op = lambda x: x[0].split(",")
        return super()._format_authors(soup_authors, sep=" ", idx=-1, op=op)


class CiteSeerX(Provider):

    re_abs = "^https?:\/\/citeseerx.ist.psu.edu\/viewdoc\/summary\?doi=(?P<doi>[0-9\.]+)"
    re_pdf = "^https?:\/\/citeseerx.ist.psu.edu\/viewdoc\/download(\;jsessionid=[A-Z0-9]+)?\?doi=(?P<doi>[0-9\.]+)&rep=rep1&type=pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = CiteSeerXInformer()
        self.server_delay = 30

        # NOTE: This is here because of this:
        # https://github.com/SeerLabs/CiteSeerX/blob/8a62545ffc904f2b41b4ecd30ce91900dc7790f4/src/java/edu/psu/citeseerx/webutils/SimpleDownloadLimitFilter.java#L136
        # The server does not allow hits to the same URL twice within a 30
        # second window. We need to hit the URL more than once to ensure it
        # redirects properly. Waiting is therefore needed.
        logger.info(
            "Waiting 30 seconds so we don't overload the CiteSeerX server."
        )
        time.sleep(30)

    def _get_doi(self, url):
        m = re.match(self.re_abs, url) or re.match(self.re_pdf, url)
        if m:
            return m["doi"]
        raise URLResolutionError(
            "CiteSeerX", url, reason="Failed to retrieve DOI."
        )

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract url from a OpenReview url """
        if re.match(self.re_abs, url):
            abs_url = url
            doi = self._get_doi(abs_url)
            pdf_url = "http://citeseerx.ist.psu.edu/viewdoc/download?doi={doi}&rep=rep1&type=pdf".format(
                doi=doi
            )
        elif re.match(self.re_pdf, url):
            pdf_url = url
            doi = self._get_doi(pdf_url)
            abs_url = "http://citeseerx.ist.psu.edu/viewdoc/summary?doi={doi}".format(
                doi=doi
            )
        else:
            raise URLResolutionError("CiteSeerX", url)
        return abs_url, pdf_url

    def validate(src):
        return re.match(CiteSeerX.re_abs, src) or re.match(
            CiteSeerX.re_pdf, src
        )
