# -*- coding: utf-8 -*-

"""Utility functions for a2r

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import PyPDF2
import requests
import string
import subprocess
import sys
import time
import unidecode

from . import GITHUB_URL
from .log import Logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 "
    "Safari/537.36"
}


logger = Logger()


def exception(msg):
    print("ERROR: " + msg, file=sys.stderr)
    print("Error occurred. Exiting.", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "If you think this might be a bug, please raise an issue on GitHub: %s"
        % GITHUB_URL
    )
    raise SystemExit(1)


def clean_string(s):
    """ Clean a string by replacing accented characters with equivalents and 
    keeping only the allowed characters (ascii letters, digits, underscore, 
    space, dash, and period)"""
    normalized = unidecode.unidecode(s)
    allowed = string.ascii_letters + string.digits + "_ .-"
    cleaned = "".join(c if c in allowed else "_" for c in normalized)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned


def assert_file_is_pdf(filename):
    """Assert that a given file is a PDF file.

    This is done by trying to open it using PyPDF2.
    """
    try:
        fp = open(filename, "rb")
        pdf = PyPDF2.PdfFileReader(fp, strict=False)
        fp.close()
        del pdf
        return True
    except PyPDF2.utils.PdfReadError:
        exception("File %s isn't a valid pdf file." % filename)


def download_url(url, filename):
    """Download the content of an url and save it to a filename """
    logger.info("Downloading file at url: %s" % url)
    content = get_page_with_retry(url)
    with open(filename, "wb") as fid:
        fid.write(content)


def get_page_with_retry(url, tries=5):
    count = 0
    while count < tries:
        count += 1
        error = False
        try:
            res = requests.get(url, headers=HEADERS)
        except requests.exceptions.ConnectionError:
            error = True
        if error or not res.ok:
            logger.warning(
                "(%i/%i) Error getting url %s. Retrying in 5 seconds."
                % (count, tries, url)
            )
            time.sleep(5)
            continue
        logger.info("Downloading url: %s" % url)
        return res.content


def upload_to_remarkable(filepath, remarkable_dir="/", rmapi_path="rmapi"):
    logger.info("Starting upload to reMarkable")

    # Create the reMarkable dir if it doesn't exist
    remarkable_dir = remarkable_dir.rstrip("/")
    if remarkable_dir:
        status = subprocess.call(
            [rmapi_path, "mkdir", remarkable_dir + "/"],
            stdout=subprocess.DEVNULL,
        )
        if not status == 0:
            exception(
                "Creating directory %s on reMarkable failed" % remarkable_dir
            )

    # Upload the file
    status = subprocess.call(
        [rmapi_path, "put", filepath, remarkable_dir + "/"],
        stdout=subprocess.DEVNULL,
    )
    if not status == 0:
        exception("Uploading file %s to reMarkable failed" % filepath)
    logger.info("Upload successful.")
