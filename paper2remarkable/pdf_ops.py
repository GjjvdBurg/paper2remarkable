# -*- coding: utf-8 -*-

"""Operations on PDF files

Author: G.J.J. van den Burg
License: See LICENSE file.
Copyright: 2019, G.J.J. van den Burg

"""


import PyPDF2
import os
import subprocess

from .crop import Cropper
from .log import Logger

logger = Logger()


def crop_pdf(filepath, pdfcrop_path="pdfcrop"):
    """Crop the pdf file using Cropper
    """
    logger.info("Cropping pdf file")
    cropped_file = os.path.splitext(filepath)[0] + "-crop.pdf"

    cropper = Cropper(filepath, cropped_file, pdfcrop_path=pdfcrop_path)
    status = cropper.crop(margins=15)

    if not status == 0:
        logger.warning("Failed to crop the pdf file at: %s" % filepath)
        return filepath
    if not os.path.exists(cropped_file):
        logger.warning(
            "Can't find cropped file '%s' where expected." % cropped_file
        )
        return filepath
    return cropped_file


def center_pdf(filepath, pdfcrop_path="pdfcrop"):
    """Center the pdf file on the reMarkable
    """
    logger.info("Centering pdf file")
    centered_file = os.path.splitext(filepath)[0] + "-center.pdf"

    cropper = Cropper(filepath, centered_file, pdfcrop_path=pdfcrop_path)
    status = cropper.center()

    if not status == 0:
        logger.warning("Failed to center the pdf file at: %s" % filepath)
        return filepath
    if not os.path.exists(centered_file):
        logger.warning(
            "Can't find centered file '%s' where expected." % centered_file
        )
        return filepath
    return centered_file


def blank_pdf(filepath):
    """Add blank pages to PDF
    """
    logger.info("Adding blank pages")
    input_pdf = PyPDF2.PdfFileReader(filepath)
    output_pdf = PyPDF2.PdfFileWriter()
    for page in input_pdf.pages:
        output_pdf.addPage(page)
        output_pdf.addBlankPage()

    output_file = os.path.splitext(filepath)[0] + "-blank.pdf"
    with open(output_file, "wb") as fp:
        output_pdf.write(fp)
    return output_file


def shrink_pdf(filepath, gs_path="gs"):
    """Shrink the PDF file size using Ghostscript
    """
    logger.info("Shrinking pdf file")
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
    return output_file
