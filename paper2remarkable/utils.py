# -*- coding: utf-8 -*-

"""Utility functions for a2r

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""


import PyPDF2
import logging
import subprocess
import sys

GITHUB_URL = "https://github.com/GjjvdBurg/arxiv2remarkable"


def exception(msg):
    print("ERROR: " + msg, file=sys.stderr)
    print("Error occurred. Exiting.", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "If you think this might be a bug, please raise an issue on GitHub: %s"
        % GITHUB_URL
    )
    raise SystemExit(1)


def check_file_is_pdf(filename):
    try:
        fp = open(filename, "rb")
        pdf = PyPDF2.PdfFileReader(fp, strict=False)
        fp.close()
        del pdf
        return True
    except PyPDF2.utils.PdfReadError:
        exception("Downloaded file isn't a valid pdf file.")


def upload_to_remarkable(filepath, remarkable_dir="/", rmapi_path="rmapi"):
    logging.info("Starting upload to reMarkable")

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
    logging.info("Upload successful.")
