# -*- coding: utf-8 -*-

"""Provider for DiVA - Digitala Vetenskapliga Arkivet

Author: G.J.J. van den Burg, Johan Holmberg
License: See LICENSE file
Copyright: 2019, 2024, G.J.J. van den Burg, Johan Holmberg

"""

import re

import bs4

from ..exceptions import FulltextMissingError
from ..exceptions import URLResolutionError
from ..log import Logger
from ..utils import get_page_with_retry
from ._base import Provider
from ._info import Informer

logger = Logger()


class DiVAInformer(Informer):
    def get_year(self, soup):
        year = soup.find("meta", {"name": "citation_publication_date"}).get(
            "content"
        )
        if not year:
            logger.warning(
                "Couldn't determine year information, maybe provide the "
                "desired filename using '--filename'?"
            )
            return ""
        return year


class DiVA(Provider):
    re_abs = r"^https?://[a-z]+.diva-portal.org/smash/record.jsf"
    re_pdf = (
        r"^https?://[a-z]+.diva-portal.org/smash/get/diva2:[0-9]+/FULLTEXT"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = DiVAInformer()

    def _get_doc_url(self, abs_url):
        page = get_page_with_retry(abs_url)
        soup = bs4.BeautifulSoup(page, "html.parser")

        pdf_url = soup.find("meta", {"name": "citation_pdf_url"})
        if pdf_url is None:
            logger.warning("Couldn't find the fulltext URL")
            raise FulltextMissingError("DiVA", abs_url)

        return pdf_url.get("content")

    def _get_abs_url(self, pdf_url):
        diva_id = re.findall("diva2:[0-9]+", pdf_url)[0].split(":")[1]
        url_candiate = re.findall(
            "https?://[a-z]+.diva-portal.org/smash/", pdf_url
        )[0]
        url_candiate += "record.jsf?pid=diva2%3A" + diva_id
        return url_candiate

    def get_abs_pdf_urls(self, url):
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = self._get_doc_url(url)
        elif re.match(self.re_pdf, url):
            abs_url = self._get_abs_url(url)
            pdf_url = url
        else:
            raise URLResolutionError("DiVA", url)
        return abs_url, pdf_url

    @staticmethod
    def validate(src):
        return re.match(DiVA.re_abs, src) or re.match(DiVA.re_pdf, src)
