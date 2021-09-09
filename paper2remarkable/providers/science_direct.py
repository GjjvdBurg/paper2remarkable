# -*- coding: utf-8 -*-

"""Provider for ScienceDirect

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2020, G.J.J. van den Burg

"""

import json
import re
import urllib

import bs4

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad

from ..exceptions import URLResolutionError
from ..log import Logger
from ..utils import get_page_with_retry
from ._base import Provider
from ._info import Informer

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
        # is retrieved by mimicking the authentication dance in Python.

        # Extract article metadata from the page
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

        if not "urlMetadata" in data:
            raise URLResolutionError("ScienceDirect", url)
        meta = data["urlMetadata"]

        # construct a temporary url to an intermediate page
        link = "{path}/{pii}/{pdfExtension}?md5{queryParams[md5]}&pid={queryParams[pid]}".format(
            **meta
        )
        tmp_url = urllib.parse.urljoin("https://sciencedirect.com/", link)

        # Open the temp url, this lands us on a page that requires Javascript
        # to do an authentication dance
        page = get_page_with_retry(tmp_url)
        soup = bs4.BeautifulSoup(page, "html.parser")
        script = soup.find_all("script")[5]
        script_text = script.decode()

        # Extract the embedded information from the script
        phrase_1 = 'i.subtle.digest("SHA-256",e("'
        try:
            rem = script_text[script_text.index(phrase_1) + len(phrase_1) :]
            token = rem[: rem.index('"')]
        except ValueError:
            raise URLResolutionError("ScienceDirect", url)

        phrase_2 = 'i.subtle.encrypt(c,t,e("'
        try:
            rem = script_text[script_text.index(phrase_2) + len(phrase_2) :]
            data = rem[: rem.index('"')]
        except ValueError:
            raise URLResolutionError("ScienceDirect", url)

        phrase_3 = 'window.location="'
        try:
            rem = script_text[script_text.index(phrase_3) + len(phrase_3) :]
            location = rem[: rem.index('",r()')]
        except ValueError:
            raise URLResolutionError("ScienceDirect", url)

        location = location.replace('"+e+"', "{e}")
        location = location.replace('"+t+"', "{t}")

        # Perform the authentication dance in Python
        e, t = self.sd_run(token, data)
        tmp_url2 = urllib.parse.urljoin(
            "https://www.sciencedirect.com", location.format(e=e, t=t)
        )

        # tmp_url2 gives a page with a ten second wait or a direct url, we need
        # the direct url
        page = get_page_with_retry(tmp_url2)
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

    def sd_e(self, e):
        n = []
        for o in range(len(e)):
            n.append(ord(e[o]))
        return n

    def sd_t(self, o):
        t = ""
        n = "0123456789abcdef"
        for r in range(len(o)):
            i = o[r]
            t += n[i >> 4] + n[15 & i]
        return t

    def sd_run(self, token, data):
        # token is the string that is passed to sha-256
        # data is the string that is passed to encrypt
        a = Random.new().read(16)
        d = self.sd_t(a)

        h = SHA256.new()
        h.update(bytearray(self.sd_e(token)))
        key = list(h.digest())

        aes = AES.new(bytearray(key), AES.MODE_CBC, iv=a)
        msg = bytearray(self.sd_e(data))
        ct_bytes = aes.encrypt(pad(msg, AES.block_size))
        ct_uint8 = list(ct_bytes)
        return d, self.sd_t(ct_uint8)
