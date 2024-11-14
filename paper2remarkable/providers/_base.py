# -*- coding: utf-8 -*-

"""Base for the Provider class

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import abc
import os
import shutil
import subprocess
import tempfile
import time

from ..exceptions import _CalledProcessError
from ..log import Logger
from ..pdf_ops import blank_pdf
from ..pdf_ops import prepare_pdf
from ..pdf_ops import shrink_pdf
from ..utils import assert_file_is_pdf
from ..utils import chdir
from ..utils import check_pdftool
from ..utils import download_url
from ..utils import follow_redirects
from ..utils import upload_to_remarkable
from ._info import Informer

logger = Logger()


class Provider(metaclass=abc.ABCMeta):
    """ABC for providers of pdf sources"""

    SUPPORTED_FORMATS = ["pdf", "ps", "epub"]
    def __init__(
        self,
        verbose=False,
        upload=True,
        debug=False,
        experimental=False,
        crop="left",
        blank=False,
        remarkable_dir="/",
        rmapi_path="rmapi",
        pdftoppm_path="pdftoppm",
        pdftk_path="pdftk",
        qpdf_path="qpdf",
        gs_path="gs",
        css=None,
        font_urls=None,
        cookiejar=None,
    ):
        self.upload = upload
        self.debug = debug
        self.experimental = experimental
        self.remarkable_dir = remarkable_dir
        self.rmapi_path = rmapi_path
        self.pdftoppm_path = pdftoppm_path
        self.pdftk_path = pdftk_path
        self.qpdf_path = qpdf_path
        self.gs_path = gs_path
        self.css = css
        self.font_urls = font_urls
        self.cookiejar = cookiejar

        self.informer = Informer()

        self.pdftool = check_pdftool(self.pdftk_path, self.qpdf_path)

        # wait time to not hit the server too frequently
        self.server_delay = 0

        # disable logging if requested
        if not verbose:
            logger.disable()

        # Define the operations to run on the pdf. Providers can add others.
        self.operations = {
            format: [] for format in self.SUPPORTED_FORMATS
        }
        self._configure_operations(crop, blank)
        logger.info("Starting %s provider" % type(self).__name__)


    def _configure_operations(self, crop, blank):
        """Configure operations for PDF and PS formats"""
        # Formats that need PDF processing
        # No processing for epubs is assumed
        pdf_formats = ['pdf', 'ps']
        def add_operation(formats, operation_name, operation_func):
            for fmt in formats:
                self.operations[fmt].append((operation_name, operation_func))

        # Base operations
        add_operation(pdf_formats, "rewrite", self.rewrite_pdf)

        # Crop operations mapping
        crop_operations = {
            'center': ('center', self.center_pdf),
            'right': ('right', self.right_pdf),
            'left': ('crop', self.crop_pdf)
        }

        # Add crop operation if specified
        if crop in crop_operations:
            add_operation(pdf_formats, *crop_operations[crop])

        # Add blank operation if specified
        if blank:
            add_operation(pdf_formats, "blank", blank_pdf)

        # PDF-specific shrink operation
        add_operation(['pdf'], "shrink", self.shrink_pdf)

    @staticmethod
    @abc.abstractmethod
    def validate(src):
        """Validate whether ``src`` is appropriate for this provider"""

    @abc.abstractmethod
    def get_abs_pdf_urls(self, src):
        """Get the url for the HTML page and the PDF file"""

    # Wrappers for pdf operations that have additional arguments
    def crop_pdf(self, filepath):
        return prepare_pdf(filepath, "crop", pdftoppm_path=self.pdftoppm_path)

    def center_pdf(self, filepath):
        return prepare_pdf(
            filepath, "center", pdftoppm_path=self.pdftoppm_path
        )

    def right_pdf(self, filepath):
        return prepare_pdf(filepath, "right", pdftoppm_path=self.pdftoppm_path)

    def shrink_pdf(self, filepath):
        return shrink_pdf(filepath, gs_path=self.gs_path)

    def retrieve_pdf(self, pdf_url, filename):
        """Download pdf from src and save to filename"""
        # This must exist so that the LocalFile provider can overwrite it
        download_url(pdf_url, filename, cookiejar=self.cookiejar)

    def compress_pdf(self, in_pdf, out_pdf):
        """Compress a pdf file, returns subprocess status"""
        if self.pdftool == "pdftk":
            status = subprocess.call(
                [self.pdftk_path, in_pdf, "output", out_pdf, "compress"]
            )
        elif self.pdftool == "qpdf":
            status = subprocess.call(
                [
                    self.qpdf_path,
                    "--stream-data=compress",
                    in_pdf,
                    out_pdf,
                ],
                stderr=subprocess.DEVNULL,
            )
        if not status == 0:
            raise _CalledProcessError(
                "%s failed to compress the PDF file." % self.pdftool
            )

    def rewrite_pdf(self, in_file, out_pdf=None):
        """Re-write the ps or pdf using Ghostscript

        This helps avoid issues in dearxiv due to nested pdfs and enables
        support for postscript files.
        """
        if out_pdf is None:
            out_pdf = os.path.splitext(in_file)[0] + "-rewrite.pdf"

        status = subprocess.call(
            [
                self.gs_path,
                "-sDEVICE=pdfwrite",
                "-dQUIET",
                "-dWriteXRefStm=false",
                "-dWriteObjStms=false",
                "-o",
                out_pdf,
                in_file,
            ]
        )
        if not status == 0:
            raise _CalledProcessError(
                "Failed to rewrite the pdf with GhostScript"
            )
        return out_pdf

    def uncompress_pdf(self, in_pdf, out_pdf):
        """Uncompress a pdf file"""
        if self.pdftool == "pdftk":
            status = subprocess.call(
                [
                    self.pdftk_path,
                    in_pdf,
                    "output",
                    out_pdf,
                    "uncompress",
                ]
            )
        elif self.pdftool == "qpdf":
            status = subprocess.call(
                [
                    self.qpdf_path,
                    "--stream-data=uncompress",
                    in_pdf,
                    out_pdf,
                ]
            )
        if not status == 0:
            raise _CalledProcessError(
                "%s failed to uncompress the PDF file." % self.pdftool
            )

    def run(self, src, filename=None):
        # follow_redirects here is needed with library use
        if os.path.exists(src):
            src = src
        elif self.cookiejar is None:
            # NOTE: We assume that if the cookiejar is not None, we are
            # properly redirected.
            src, self.cookiejar = follow_redirects(src)
            time.sleep(self.server_delay)

        # extract page and pdf file urls
        abs_url, pdf_url = self.get_abs_pdf_urls(src)

        # generate nice filename if needed
        clean_filename = filename or self.informer.get_filename(abs_url)
        extension = clean_filename.split(".")[-1]
        tmp_filename = f"paper.{extension}"

        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format {extension}. Must be one of {self.SUPPORTED_FORMATS}")


        self.initial_dir = os.getcwd()
        with tempfile.TemporaryDirectory(prefix="p2r_") as working_dir:
            with chdir(working_dir):
                self.retrieve_pdf(pdf_url, tmp_filename)

                if extension in "pdf ps".split():
                    assert_file_is_pdf(tmp_filename)

                intermediate_fname = tmp_filename
                for opname, op in self.operations[extension]:
                    intermediate_fname = op(intermediate_fname)

                shutil.copy(intermediate_fname, clean_filename)

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
