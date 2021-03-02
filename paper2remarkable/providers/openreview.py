# -*- coding: utf-8 -*-

"""Provider for OpenReview

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import json
import re

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError
from ..log import Logger

logger = Logger()


class OpenReviewInformer(Informer):

    meta_date_key = "citation_publication_date"

    def get_authors(self, soup):
        # Get the authors for OpenReview by parsing the JSON payload
        #
        # This may not be super robust long term, but works for now.
        warning = (
            "Couldn't determine author information, maybe provide "
            "the desired filename using '--filename'?"
        )

        script = soup.find("script", {"id": "__NEXT_DATA__"})
        if not script:
            logger.warning(warning)
            return ""

        try:
            paper_data = json.loads(script.contents[0])
        except json.JSONDecodeError:
            logger.warning(warning)
            return ""

        try:
            content = paper_data["props"]["pageProps"]["forumNote"]["content"]
            authors = content["authors"]
        except KeyError:
            logger.warning(warning)
            return ""
        return self._format_authors(authors)

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
