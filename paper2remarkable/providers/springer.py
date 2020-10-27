# -*- coding: utf-8 -*-

"""Provider for Springer

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import re
import urllib
import requests

from ._base import Provider
from ._info import Informer
from ..exceptions import URLResolutionError
from ..utils import HEADERS


class SpringerInformer(Informer):

    meta_date_key = None

    def _format_authors(self, soup_authors):
        return super()._format_authors(soup_authors, sep=" ", idx=-1)

    def get_year(self, soup):
        for key in ["citation_online_date", "citation_publication_date"]:
            meta = soup.find_all("meta", {"name": key})
            if not meta:
                continue
            return self._format_year(meta[0]["content"])
        return ""


class Springer(Provider):

    re_abs_1 = "https?:\/\/link.springer.com\/article\/10\.\d{4}\/[a-z0-9\-]+"
    re_abs_2 = "https?:\/\/link.springer.com\/chapter\/10\.\d{4}\/[a-z0-9\-]+"
    re_pdf = "https?:\/\/link\.springer\.com\/content\/pdf\/10\.\d{4}(%2F|\/)[a-z0-9\-\_]+\.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = SpringerInformer()

    def _get_abs_url(self, pdf_url):
        article_url = pdf_url.replace("content/pdf", "article")[: -len(".pdf")]
        req = requests.head(
            article_url, headers=HEADERS, cookies=self.cookiejar
        )
        if req.status_code == 200:
            return article_url

        chapter_url = pdf_url.replace("content/pdf", "chapter")[: -len(".pdf")]
        req = requests.head(
            chapter_url, headers=HEADERS, cookies=self.cookiejar
        )
        if req.status_code == 200:
            return chapter_url

        raise URLResolutionError("Springer", pdf_url)

    def get_abs_pdf_urls(self, url):
        """ Get the pdf and abstract urls from a Springer url """
        if re.match(self.re_abs_1, url):
            abs_url = url
            pdf_url = url.replace("article", "content/pdf")
        elif re.match(self.re_abs_2, url):
            abs_url = url
            pdf_url = url.replace("chapter", "content/pdf")
        elif re.match(self.re_pdf, url):
            abs_url = self._get_abs_url(url)
            pdf_url = urllib.parse.unquote(url)
        else:
            raise URLResolutionError("Springer", url)
        return abs_url, pdf_url

    def validate(src):
        return (
            re.match(Springer.re_abs_1, src)
            or re.match(Springer.re_abs_2, src)
            or re.match(Springer.re_pdf, src)
        )
