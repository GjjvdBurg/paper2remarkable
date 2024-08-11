# -*- coding: utf-8 -*-

"""Operations on PDF files

Author: G.J.J. van den Burg
License: See LICENSE file.
Copyright: 2019, G.J.J. van den Burg

"""


import os
import subprocess

from pikepdf import Pdf

from .crop import Cropper
from .log import Logger

logger = Logger()


def prepare_pdf(filepath, operation, pdftoppm_path="pdftoppm"):
    """Prepare pdf by cropping, centering, or right-aligning the flie"""
    logger.info("Preparing PDF using %s operation" % operation)
    prepared_file = os.path.splitext(filepath)[0] + "-prep.pdf"
    cropper = Cropper(filepath, prepared_file, pdftoppm_path=pdftoppm_path)
    if operation == "crop":
        status = cropper.crop(margins=15)
    elif operation == "center":
        status = cropper.center()
    elif operation == "right":
        status = cropper.right()
    else:
        logger.warning("Unknown operation: %s" % operation)
        return filepath
    if not status == 0 or not os.path.exists(prepared_file):
        logger.warning("PDF prepare operation failed")
        return filepath
    return prepared_file


def blank_pdf(filepath):
    """Add blank pages to PDF"""
    logger.info("Adding blank pages")
    pdf = Pdf.open(filepath)
    # Note: creating a new file doesn't keep the table of contents, but it
    # would anyway be incorrect when adding blank pages
    dst = Pdf.new()
    for page in pdf.pages:
        dst.pages.append(page)
        x0, y0, x1, y1 = page.MediaBox
        dst.add_blank_page(page_size=(x1 - x0, y1 - y0))
    output_file = os.path.splitext(filepath)[0] + "-blank.pdf"
    dst.save(output_file)
    return output_file


def _filesize_string(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def shrink_pdf(filepath, gs_path="gs"):
    """Shrink the PDF file size using Ghostscript"""
    logger.info("Shrinking pdf file ...")
    size_before = os.path.getsize(filepath)
    output_file = os.path.splitext(filepath)[0] + "-shrink.pdf"
    status = subprocess.call(
        [
            gs_path,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/printer",
            "-dNOPAUSE",
            "-dBATCH",
            "-dQUIET",
            "-sOutputFile=%s" % output_file,
            filepath,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not status == 0:
        logger.warning("Failed to shrink the pdf file")
        return filepath

    size_after = os.path.getsize(output_file)
    if size_after > size_before:
        size_str = _filesize_string(size_before)
        logger.info(
            f"Shrinking has no effect for this file, using original ({size_str})."
        )
        return filepath
    size_str = _filesize_string(size_after)
    logger.info(f"Shrinking brought filesize down to {size_str}")
    return output_file
