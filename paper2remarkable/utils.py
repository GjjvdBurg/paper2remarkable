# -*- coding: utf-8 -*-

"""Utility functions for a2r

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import regex
import requests
import string
import subprocess
import time
import unidecode

from pikepdf import Pdf, PdfError

from .log import Logger
from .exceptions import FileTypeError, NoPDFToolError

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 "
    "Safari/537.36"
}


logger = Logger()


def clean_string(s):
    """Clean a string by replacing accented characters with equivalents and
    keeping only the allowed characters (ascii letters, digits, underscore,
    space, dash, and period)"""
    normalized = unidecode.unidecode(s)
    allowed = string.ascii_letters + string.digits + "_ .-"
    cleaned = "".join(c if c in allowed else "_" for c in normalized)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    cleaned = cleaned.strip("_")
    return cleaned


def assert_file_is_pdf(filename):
    """Assert that a given file is a PDF file.

    This is done by trying to open it using pikepdf.
    """
    try:
        pdf = Pdf.open(filename)
        pdf.close()
        del pdf
        return True
    except PdfError:
        raise FileTypeError(filename, "pdf")


def download_url(url, filename, cookiejar=None):
    """Download the content of an url and save it to a filename """
    logger.info("Downloading file at url: %s" % url)
    content = get_page_with_retry(url, cookiejar=cookiejar)
    with open(filename, "wb") as fid:
        fid.write(content)


def get_page_with_retry(url, tries=5, cookiejar=None, return_text=False):
    count = 0
    jar = {} if cookiejar is None else cookiejar
    while count < tries:
        count += 1
        error = False
        try:
            res = requests.get(url, headers=HEADERS, cookies=jar)
        except requests.exceptions.ConnectionError:
            error = True
        if error or not res.ok:
            logger.warning(
                "(%i/%i) Error getting url %s. Retrying in 5 seconds."
                % (count, tries, url)
            )
            time.sleep(5)
            continue
        logger.info("Downloaded url: %s" % url)
        if return_text:
            return res.text
        return res.content


def get_content_type_with_retry(url, tries=5, cookiejar=None):
    if cookiejar is None:
        jar = requests.cookies.RequestsCookieJar()
    else:
        jar = cookiejar

    msg = "(%i/%i) Error getting content type for %s. Retrying in 5 seconds."

    # In rare cases, a HEAD request fails but a GET request does work. So here
    # we try both
    ops = [requests.head, requests.get]
    kwargs = dict(headers=HEADERS, cookies=jar, allow_redirects=True)
    for op in ops:
        count = 0
        while count < tries:
            count += 1
            error = False
            try:
                res = op(url, **kwargs)
            except requests.exceptions.ConnectionError:
                error = True
            if error or not res.ok:
                logger.warning(msg % (count, tries, url))
                time.sleep(5)
                continue
            return res.headers.get("Content-Type", None)
    return None


def follow_redirects(url):
    """Follow redirects from the URL (at most 100)"""
    it = 0
    jar = requests.cookies.RequestsCookieJar()
    while it < 100:
        req = requests.head(
            url, headers=HEADERS, allow_redirects=False, cookies=jar
        )
        if req.status_code == 200:
            break
        if not "Location" in req.headers:
            break
        url = req.headers["Location"]
        jar.update(req.cookies)
        it += 1
    if it == 100:
        logger.warning("Max redirects reached. There may be a problem.")
    jar = jar or req.cookies
    return url, jar


def is_url(string):
    # pattern adapted from CleverCSV
    pattern = "((https?|ftp):\/\/(?!\-))?(((([\p{L}\p{N}]*[\-\_]?[\p{L}\p{N}]+)+\.)+([a-z]{2,}|local)(\.[a-z]{2,3})?)|localhost|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\:\d{1,5})?))(\/[\p{L}\p{N}_\/()~?=&%\-\#\.:+]*)?(\.[a-z]+)?"
    string = string.strip(" ")
    match = regex.fullmatch(pattern, string)
    return match is not None


def check_pdftool(pdftk_path, qpdf_path):
    """Check whether we have pdftk or qpdf available"""
    # set defaults in case either is set to None or something
    pdftk_path = pdftk_path or "false"
    qpdf_path = qpdf_path or "false"

    try:
        status = subprocess.call(
            [pdftk_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        status = 1
    if status == 0:
        return "pdftk"
    try:
        status = subprocess.call(
            [qpdf_path, "--help"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        status = 1
    if status == 0:
        return "qpdf"
    raise NoPDFToolError
