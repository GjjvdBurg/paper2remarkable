# -*- coding: utf-8 -*-

"""Provider for ScienceDirect

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import re
import bs4
import urllib
import json

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError
from ..log import Logger
from ..utils import get_page_with_retry, follow_redirects

logger = Logger()


class ScienceDirectInformer(Informer):

    meta_date_key = "citation_publication_date"

    def get_authors(self, soup):
        surname_tags = soup.find_all("span", attrs={"class": "text surname"})
        if not surname_tags:
            logger.warning(
                "Couldn't determine author information, maybe provide the desired filename using '--filename'?"
            )
            return ""
        authors = [x.text for x in surname_tags]
        return authors


class ScienceDirect(Provider):

    re_abs = (
        "https?:\/\/www.sciencedirect.com/science/article/pii/[A-Za-z0-9]+"
    )
    re_pdf = "https://pdf.sciencedirectassets.com/\d+/([0-9a-zA-Z\-\.]+)/(?P<data>[0-9a-zA-Z\-\.]+)/main.pdf\?.*"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = ScienceDirectInformer()

    def get_abs_pdf_urls(self, url):
        m1 = re.match(self.re_abs, url)
        m2 = re.match(self.re_pdf, url)
        if m1:
            abs_url = url
            pdf_url = self._get_pdf_url(abs_url)
        elif m2:
            pdf_url = url
            data = m2.group("data")
            paper_id = data.split("-")[-1]
            abs_url = (
                f"https://www.sciencedirect.com/science/article/pii/{paper_id}"
            )
        else:
            raise URLResolutionError("ScienceDirect", url)
        return abs_url, pdf_url

    def _get_pdf_url(self, url):
        page = get_page_with_retry(url)
        soup = bs4.BeautifulSoup(page, "html.parser")

        # For open access (and maybe behind institution?) the full text pdf url
        # is currently in the json payload of a script tag.
        scripts = soup.find_all("script", attrs={"data-iso-key": "_0"})
        if not scripts:
            raise URLResolutionError("ScienceDirect", url)
        json_data = scripts[0].string
        data = json.loads(json_data)
        if not "article" in data:
            raise URLResolutionError("ScienceDirect", url)
        data = data["article"]
        if not "pdfDownload" in data:
            raise URLResolutionError("ScienceDirect", url)
        data = data["pdfDownload"]
        if not "linkToPdf" in data:
            raise URLResolutionError("ScienceDirect", url)
        link = data["linkToPdf"]
        tmp_url = urllib.parse.urljoin("https://sciencedirect.com/", link)

        # tmp_url gives a page with a ten second wait or a direct url, we need
        # the direct url
        page = get_page_with_retry(tmp_url)
        soup = bs4.BeautifulSoup(page, "html.parser")
        noscript = soup.find_all("noscript")
        if not noscript:
            raise URLResolutionError("ScienceDirect", url)
        a = noscript[0].find_all("a")
        if not a:
            raise URLResolutionError("ScienceDirect", url)
        pdf_url = a[0].get("href")
        return pdf_url

    def validate(src):
        return re.match(ScienceDirect.re_abs, src) or re.match(
            ScienceDirect.re_pdf, src
        )
