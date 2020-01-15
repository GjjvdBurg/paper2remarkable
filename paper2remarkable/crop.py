# -*- coding: utf-8 -*-

"""Code for cropping a PDF file

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import PyPDF2
import os
import subprocess
import pdfplumber

from .log import Logger

RM_WIDTH = 1404
RM_HEIGHT = 1872

logger = Logger()


class Cropper(object):
    def __init__(
        self, input_file=None, output_file=None, pdfcrop_path="pdfcrop"
    ):
        if not input_file is None:
            self.input_file = os.path.abspath(input_file)
            self.reader = PyPDF2.PdfFileReader(self.input_file)
        if not output_file is None:
            self.output_file = os.path.abspath(output_file)
        self.pdfcrop_path = pdfcrop_path

        self.writer = PyPDF2.PdfFileWriter()

    def crop(self, margins=1):
        return self.process_file(self.crop_page, margins=margins)

    def center(self, padding=15):
        return self.process_file(self.center_page, padding=padding)

    def process_file(self, page_func, *args, **kwargs):
        n = self.reader.getNumPages()
        for page_idx in range(n):
            status = page_func(page_idx, *args, **kwargs)
            if not status == 0:
                return status
            if (page_idx + 1) % 10 == 0:
                logger.info("Processing pages ... (%i/%i)" % (page_idx + 1, n))
        with open(self.output_file, "wb") as fp:
            self.writer.write(fp)
        logger.info("Processing pages ... (%i/%i)" % (n, n))
        return 0

    def center_page(self, page_idx, padding):
        return self.process_page(
            page_idx, self.get_center_bbox, padding=padding
        )

    def crop_page(self, page_idx, margins):
        return self.process_page(page_idx, self.get_bbox, margins=margins)

    def export_page(self, page_idx):
        """Helper function that exports a single page given by index """
        page = self.reader.getPage(page_idx)
        writer = PyPDF2.PdfFileWriter()
        writer.addPage(page)
        tmpfname = "./page.pdf"
        with open(tmpfname, "wb") as fp:
            writer.write(fp)
        return tmpfname

    def process_page(self, page_idx, bbox_func, *args, **kwargs):
        """Process a single page and add it to the writer """
        tmpfname = self.export_page(page_idx)
        tmpfout = "./output.pdf"
        bbox = bbox_func(tmpfname, *args, **kwargs)
        status = subprocess.call(
            [
                self.pdfcrop_path,
                "--bbox",
                " ".join(map(str, bbox)),
                tmpfname,
                tmpfout,
            ],
            stdout=subprocess.DEVNULL,
        )
        if not status == 0:
            return status
        reader = PyPDF2.PdfFileReader(tmpfout)
        page = reader.getPage(0)
        self.writer.addPage(page)
        os.unlink(tmpfname)
        os.unlink(tmpfout)
        return 0

    def get_bbox(self, filename, margins=1, resolution=72):
        """Get the bounding box, with optional margins

        if margins is integer, used for all margins, else
        margins = [left, top, right, bottom]

        We get the bounding box by finding the smallest rectangle that is 
        completely surrounded by white pixels.
        """
        if isinstance(margins, int):
            margins = [margins for _ in range(4)]
        pdf = pdfplumber.open(filename)
        im = pdf.pages[0].to_image(resolution=resolution)
        pdf.close()

        pixels = list(im.original.getdata())
        W, H = im.original.size

        # M is a list of H lists with each W integers that equal the sum of the
        # pixel values
        M = [[sum(x) for x in pixels[i * W : (i + 1) * W]] for i in range(H)]

        left, top, bottom, right = 0, 0, 0, 0
        while top < H and sum(M[top]) == W * 255 * 3:
            top += 1
        while bottom < H and sum(M[H - 1 - bottom]) == W * 255 * 3:
            bottom += 1

        # Transpose M
        M = list(zip(*M))
        while left < W and sum(M[left]) == H * 255 * 3:
            left += 1
        while right < W and sum(M[W - 1 - right]) == H * 255 * 3:
            right += 1

        left -= margins[0]
        top -= margins[1]
        right -= margins[2]
        bottom -= margins[3]

        # This is the bounding box in PIL format: (0, 0) top left
        x0, y0, x1, y1 = left, top, W - right, H - bottom

        # Get the bbox in Ghostscript format: (0, 0) bottom left
        a0, b0, a1, b1 = x0, H - y1, x1, H - y0
        return [a0, b0, a1, b1]

    def get_center_bbox(self, filename, padding=15):
        """Compute a bounding box that will center the page file on the 
        reMarkable
        """
        bbox = self.get_bbox(filename, margins=0)

        h = bbox[3] - bbox[1]
        w = bbox[2] - bbox[0]

        # we want some minimal padding all around, because it is visually more
        # pleasing.
        h_prime = h + 2 * padding
        w_prime = w + 2 * padding

        # if the document is wider than the remarkable, we add top-padding to
        # center it, otherwise we add left-padding
        x, y = 0, 0
        if h_prime / w_prime < RM_HEIGHT / RM_WIDTH:
            y = ((RM_HEIGHT / RM_WIDTH) * w_prime - h_prime) / 2
        else:
            x = ((RM_WIDTH / RM_HEIGHT) * h_prime - w_prime) / 2

        margins = [padding + x, padding + y, padding, padding]
        return self.get_bbox(filename, margins=margins)
