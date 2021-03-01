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
        logger.info("Shrinking has no effect for this file, using original.")
        return filepath
    return output_file


def copy_toc(toc, filepath):
    logger.info("Copying table of content ...")
    reader = PyPDF2.PdfFileReader(filepath)
    output_pdf = PyPDF2.PdfFileWriter()
    output_pdf.cloneDocumentFromReader(reader)

    # It holds the corresponding bookmark for the last level seen, which will be retrieved to
    # specify the parent when we add the bookmark, to generate nested bookmarks.
    # It assumes the table of content is well constructed and doesn't jump from a level 1 to a
    # level 3 title without going through a level 2 at first. If it does, the parent bookmark
    # associated to the level 3 could be wrong if we saw a level 2 previously (but not the right
    # now obviously).
    level_last_bookmarks = {}

    for level, page, title in toc:
        parent = None
        if level > 0:
            parent = level_last_bookmarks.get(level - 1)

        bookmark = output_pdf.addBookmark(title, page, parent=parent, fit="/Fit")
        level_last_bookmarks[level] = bookmark

    output_file = os.path.splitext(filepath)[0] + "-with-toc.pdf"
    with open(output_file, "wb") as f:
        output_pdf.write(f)

    return output_file


def get_toc(filepath):
    input_pdf = PyPDF2.PdfFileReader(filepath)
    return list(yield_outlines(input_pdf, input_pdf.getOutlines()))


def yield_outlines(reader, outlines, level=0):
    if isinstance(outlines, list):
        for item in outlines:
            yield from yield_outlines(reader, item, level=level + 1)
    else:
        page_number = reader.getDestinationPageNumber(outlines)
        yield level, page_number, outlines["/Title"]
