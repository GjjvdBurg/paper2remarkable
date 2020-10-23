# -*- coding: utf-8 -*-

"""Code for cropping a PDF file

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import PyPDF2
import io
import os
import pdfplumber
import subprocess

from PyPDF2.generic import RectangleObject

from .log import Logger

RM_WIDTH = 1404
RM_HEIGHT = 1872

logger = Logger()


def find_offset_byte_line(line):
    """Find index of first nonzero bit in a line of bytes

    The given line is a string of bytes, each representing 8 pixels. This code
    finds the index of the first bit that is not zero. Used when finding the
    cropbox with pdftoppm.
    """
    off = 0
    for c in line:
        if c == 0:
            off += 8
        else:
            k = 0
            while c > 0:
                k += 1
                c >>= 1
            off += k
            break
    return off


def check_pdftoppm(pth):
    """Check that we can run the provided pdftoppm executable"""
    try:
        subprocess.check_output([pth, "-v"], stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
        logger.info("pdftoppm not found, using pdfplumber instead (slower)")
        return False
    return True


class Cropper(object):
    def __init__(
        self,
        input_file=None,
        output_file=None,
        pdftoppm_path="pdftoppm",
    ):
        if not input_file is None:
            self.input_file = os.path.abspath(input_file)
            self.reader = PyPDF2.PdfFileReader(self.input_file)
        if not output_file is None:
            self.output_file = os.path.abspath(output_file)

        if pdftoppm_path and not check_pdftoppm(pdftoppm_path):
            pdftoppm_path = None

        self.pdftoppm_path = pdftoppm_path
        self.writer = PyPDF2.PdfFileWriter()

    def crop(self, margins=1):
        return self.process_file(self.crop_page, margins=margins)

    def center(self, padding=15):
        return self.process_file(self.center_page, padding=padding)

    def right(self, padding=15):
        return self.process_file(self.right_page, padding=padding)

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
        if n % 10 > 0:
            logger.info("Processing pages ... (%i/%i)" % (n, n))
        return 0

    def crop_page(self, page_idx, margins):
        return self.process_page(page_idx, self.get_bbox, margins=margins)

    def center_page(self, page_idx, padding):
        return self.process_page(
            page_idx, self.get_center_bbox, padding=padding
        )

    def right_page(self, page_idx, padding):
        return self.process_page(
            page_idx, self.get_right_bbox, padding=padding
        )

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
        bbox = bbox_func(tmpfname, *args, **kwargs)
        thepage = self.reader.getPage(page_idx)
        thepage.cropBox = RectangleObject(bbox)
        self.writer.addPage(thepage)
        os.unlink(tmpfname)
        return 0

    def get_raw_bbox(self, filename, resolution=72):
        """Get the basic bounding box of a pdf file"""
        if self.pdftoppm_path is None:
            box = self.get_raw_bbox_pdfplumber(filename, resolution=resolution)
        else:
            box = self.get_raw_bbox_pdftoppm(filename, resolution=resolution)
        return box

    def get_raw_bbox_pdfplumber(self, filename, resolution=72):
        """Get the basic bounding box with pdfplumber"""
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

        return left, right, top, bottom, W, H

    def get_raw_bbox_pdftoppm(self, filename, resolution=72):
        """Get the basic bounding box using pdftoppm """
        cmd = [
            self.pdftoppm_path,
            "-r",
            str(resolution),
            "-singlefile",
            "-mono",
            filename,
        ]

        im = subprocess.check_output(cmd)
        im = io.BytesIO(im)

        id_ = im.readline().rstrip(b"\n")
        if not id_ == b"P4":
            raise ValueError("Not in P4 format")
        wh = im.readline().rstrip(b"\n").split(b" ")
        width, height = int(wh[0]), int(wh[1])
        imdata = im.read()

        pad = width % 8
        padwidth = width + pad
        stepsize = padwidth // 8

        for top in range(height):
            if sum(imdata[top * stepsize : (top + 1) * stepsize]) > 0:
                break

        for bottom in reversed(range(height)):
            if sum(imdata[bottom * stepsize : (bottom + 1) * stepsize]) > 0:
                break

        left = width
        right = 0
        for i in range(top, bottom):
            lline = imdata[i * stepsize : (i + 1) * stepsize]
            rline = reversed(imdata[i * stepsize : (i + 1) * stepsize])
            l = find_offset_byte_line(lline)
            left = min(left, l)
            r = padwidth + pad - find_offset_byte_line(rline)
            right = max(right, r)

        top += 1
        left += 1
        right = width - right + 2
        bottom = height - bottom - 2

        return left, right, top, bottom, width, height

    def get_bbox(self, filename, margins=1, resolution=72):
        """Get the bounding box, with optional margins

        if margins is integer, used for all margins, else
        margins = [left, top, right, bottom]

        We get the bounding box by finding the smallest rectangle that is
        completely surrounded by white pixels.
        """
        if isinstance(margins, int):
            margins = [margins for _ in range(4)]

        left, right, top, bottom, W, H = self.get_raw_bbox(
            filename, resolution=resolution
        )

        left -= margins[0]
        left = max(left, 0)
        top -= margins[1]
        top = max(top, 0)
        right -= margins[2]
        bottom -= margins[3]

        # This is the bounding box in PIL format: (0, 0) top left
        x0, y0, x1, y1 = left, top, W - right, H - bottom

        # The remarkable changes the orientation of a portrait page if the
        # width is greater than the height. To prevent this, we pad the height
        # with extra whitespace. This should only occur if the original
        # orientation of the page would be changed by cropping.
        w, h = x1 - x0, y1 - y0
        if H > W and w > h:
            y1 = y0 + w + 10
            h = y1 - y0

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
        x = y = 0
        if h_prime / w_prime < RM_HEIGHT / RM_WIDTH:
            y = ((RM_HEIGHT / RM_WIDTH) * w_prime - h_prime) / 2
        else:
            x = ((RM_WIDTH / RM_HEIGHT) * h_prime - w_prime) / 2

        margins = [padding + x, padding + y, padding, padding]
        return self.get_bbox(filename, margins=margins)

    def get_right_bbox(self, filename, padding=15):
        """Get the bounding box that ensures the menu doesn't hide the text"""

        bbox = self.get_bbox(filename, margins=0)

        h = bbox[3] - bbox[1]
        w = bbox[2] - bbox[0]

        # Note, the menu width is about 12mm and the entire screen is about
        # 156mm. This informs the width of the left padding we'll add.
        menu_width = 12 / 156 * RM_WIDTH

        H = RM_HEIGHT
        W = RM_WIDTH

        # TODO: This math is approximate. The goal is to get the page centered
        # in the remaining space after taking the menu width into account,
        # while also providing equal padding at the top and bottom. This seems
        # to give too much padding on the left for some pages, but I'm not sure
        # why. Pull requests welcome!
        rho_rm = H / (W - menu_width)
        rho_page = (h + 2 * padding) / (w + 2 * padding)
        x = y = 0
        if rho_rm < rho_page:
            x = -w - 2 * padding + (h + 2 * padding) * (W - menu_width) / H
        elif rho_rm > rho_page:
            y = -h - 2 * padding + H * (w + 2 * padding) / (W - menu_width)

        margins = [
            menu_width + x + padding,
            padding + y,
            padding,
            padding,
        ]
        return self.get_bbox(filename, margins=margins)
