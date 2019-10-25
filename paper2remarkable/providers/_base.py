# -*- coding: utf-8 -*-

"""Base for the Provider class

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import abc
import os
import shutil
import tempfile

from ._info import Informer
from ..pdf_ops import crop_pdf, center_pdf, blank_pdf, shrink_pdf
from ..utils import assert_file_is_pdf, download_url, upload_to_remarkable
from ..log import Logger

logger = Logger()


class Provider(metaclass=abc.ABCMeta):
    """ ABC for providers of pdf sources """

    def __init__(
        self,
        verbose=False,
        upload=True,
        debug=False,
        center=False,
        blank=False,
        remarkable_dir="/",
        rmapi_path="rmapi",
        pdfcrop_path="pdfcrop",
        pdftk_path="pdftk",
        gs_path="gs",
    ):
        self.upload = upload
        self.debug = debug
        self.remarkable_dir = remarkable_dir
        self.rmapi_path = rmapi_path
        self.pdfcrop_path = pdfcrop_path
        self.pdftk_path = pdftk_path
        self.gs_path = gs_path
        self.informer = Informer()

        # disable logging if requested
        if not verbose:
            logger.disable()

        # Define the operations to run on the pdf. Providers can add others.
        self.operations = [("crop", self.crop_pdf)]
        if center:
            self.operations.append(("center", self.center_pdf))

        if blank:
            self.operations.append(("blank", blank_pdf))
        self.operations.append(("shrink", self.shrink_pdf))

        logger.info("Starting %s" % type(self).__name__)

    @staticmethod
    @abc.abstractmethod
    def validate(src):
        """ Validate whether ``src`` is appropriate for this provider """

    # Wrappers for pdf operations that have additional arguments
    def crop_pdf(self, filepath):
        return crop_pdf(filepath, pdfcrop_path=self.pdfcrop_path)

    def center_pdf(self, filepath):
        return center_pdf(filepath, pdfcrop_path=self.pdfcrop_path)

    def shrink_pdf(self, filepath):
        return shrink_pdf(filepath, gs_path=self.gs_path)

    def retrieve_pdf(self, pdf_url, filename):
        """ Download pdf from src and save to filename """
        # This must exist so that the LocalFile provider can overwrite it
        download_url(pdf_url, filename)

    def run(self, src, filename=None):
        abs_url, pdf_url = self.get_abs_pdf_urls(src)
        clean_filename = filename or self.informer.get_filename(abs_url)
        tmp_filename = "paper.pdf"

        self.initial_dir = os.getcwd()
        with tempfile.TemporaryDirectory(prefix="p2r_") as working_dir:
            os.chdir(working_dir)
            self.retrieve_pdf(pdf_url, tmp_filename)
            assert_file_is_pdf(tmp_filename)

            intermediate_fname = tmp_filename
            for opname, op in self.operations:
                intermediate_fname = op(intermediate_fname)
            shutil.move(intermediate_fname, clean_filename)

            if self.debug:
                print("Paused in debug mode in dir: %s" % working_dir)
                print("Press enter to exit.")
                return input()

            if self.upload:
                return upload_to_remarkable(
                    clean_filename,
                    remarkable_dir=self.remarkable_dir,
                    rmapi_path=self.rmapi_path,
                )

            target_path = os.path.join(self.initial_dir, clean_filename)
            while os.path.exists(target_path):
                base = os.path.splitext(target_path)[0]
                target_path = base + "_.pdf"
            shutil.move(clean_filename, target_path)
            return target_path
