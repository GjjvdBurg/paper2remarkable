# -*- coding: utf-8 -*-

"""Code for adjusting view

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2021, G.J.J. van den Burg

"""

from collections import namedtuple

from .crop import Cropper

# This is an experimental module that aims to use the reMarkable's own file
# format to adjust the view of a PDF, instead of setting the bounding box as is
# done in the "Cropper". At the moment this is work in progress.
#
# To the best of my knowledge the content file format of the reMarkable is not
# extensively documented outside what is available
# [here](https://remarkablewiki.com/tech/filesystem#content_file_format). This
# module will mainly rely on the "transform" attribute, which is largely
# undocumented.
#
# TODO:
#  - Figure out what m31 and m32 do in the "transform".
#  - Test if we can reliably do left/center/right crops using transforms.
#  - Add a UI flag to use adjust instead of crop (as well as config option)
#  - Figure out how to deliver a ZIP instead of a PDF using rmapi/rmapy


class Transform:
    def __init__(self, transform=None):
        self.transform = transform or self._default_transform()

    def _default_transform(self):
        keys = ["m%i%i" % (i, j) for i in range(3) for j in range(3)]
        keys.sort()
        transform = {k: 0 for k in keys}
        transform["m11"] = transform["m22"] = transform["m33"] = 1
        return transform


# (0, 0) bottom left: so xmin = left margin, xmax is margin + content
BBox = namedtuple("BBox", ["xmin", "xmax", "ymin", "ymax"])

PageDims = namedtuple("PageDims", ["width", "height"])


class Adjuster:
    def __init__(self, input_file, pdftoppm_path="pdftoppm"):
        self.cropper = Cropper(
            input_file=input_file, pdftoppm_path=pdftoppm_path
        )

    def left(self, margins=1) -> Transform:
        return self.process_file(kind="left", margins=margins)

    def center(self, padding=15) -> Transform:
        return self.process_file(kind="center", padding=padding)

    def right(self, padding=15) -> Transform:
        return self.process_file(kind="right", padding=padding)

    def process_file(self, kind="left", **kwargs):
        outerbbox = BBox(
            xmin=float("inf"),
            xmax=-float("inf"),
            ymin=float("inf"),
            ymax=-float("inf"),
        )
        outerpage = PageDims(-float("inf"), -float("inf"))

        for page_idx in range(self.cropper.reader.getNumPages()):
            tmpfname = self.cropper.export_page(page_idx)
            raw_bbox = self.cropper.get_raw_bbox(tmpfname)
            page_dims = PageDims(width=raw_bbox[4], height=raw_bbox[5])

            if kind == "left":
                bbox = self.cropper.get_bbox(tmpfname, **kwargs)
            elif kind == "center":
                bbox = self.cropper.get_center_bbox(tmpfname, **kwargs)
            elif kind == "right":
                bbox = self.cropper.get_right_bbox(tmpfname, **kwargs)
            else:
                raise ValueError(f"Unknown crop type: {kind}")

            page_bbox = BBox(
                xmin=bbox[0], xmax=bbox[2], ymin=bbox[1], ymax=bbox[3]
            )

            outerbbox.xmin = min(outerbbox.xmin, page_bbox.xmin)
            outerbbox.ymin = min(outerbbox.ymin, page_bbox.ymin)
            outerbbox.xmax = max(outerbbox.xmax, page_bbox.xmax)
            outerbbox.ymax = max(outerbbox.ymax, page_bbox.ymax)

            outerpage.width = max(outerpage.width, page_dims.width)
            outerpage.height = max(outerpage.height, page_dims.height)

        bbox_width = outerbbox.xmax - outerbbox.xmin
        bbox_height = outerbbox.ymax - outerbbox.ymin

        transform = Transform()
        transform["m11"] = outerpage.height / bbox_height
        transform["m22"] = outerpage.width / bbox_width
        # TODO Figure out what m31 and m32 do, they're likely offsets
        return transform
