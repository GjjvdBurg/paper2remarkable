# -*- coding: utf-8 -*-

"""Provider for arxiv.org

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import os
import re
import subprocess

from ._info import Informer
from ._base import Provider
from ..exceptions import (
    URLResolutionError,
    _CalledProcessError as CalledProcessError,
)
from ..log import Logger

logger = Logger()

DEARXIV_TEXT_REGEX = (
    b"arXiv:\d{4}\.\d{4,5}v\d+\s+\[[\w\-]+\.\w+\]\s+\d{1,2}\s\w{3}\s\d{4}"
)


class ArxivInformer(Informer):
    pass


class Arxiv(Provider):

    re_abs = "https?://arxiv.org/abs/\d{4}\.\d{4,5}(v\d+)?"
    re_pdf = "https?://arxiv.org/pdf/\d{4}\.\d{4,5}(v\d+)?\.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = ArxivInformer()

        # register the dearxiv operation
        self.operations.insert(0, ("dearxiv", self.dearxiv))

    def get_abs_pdf_urls(self, url):
        """Get the pdf and abs url from any given arXiv url """
        if re.match(self.re_abs, url):
            abs_url = url
            pdf_url = url.replace("abs", "pdf") + ".pdf"
        elif re.match(self.re_pdf, url):
            abs_url = url[:-4].replace("pdf", "abs")
            pdf_url = url
        else:
            raise URLResolutionError("arXiv", url)
        return abs_url, pdf_url

    def validate(src):
        """Check if the url is to an arXiv page. """
        return re.match(Arxiv.re_abs, src) or re.match(Arxiv.re_pdf, src)

    def dearxiv(self, input_file):
        """Remove the arXiv timestamp from a pdf"""
        logger.info("Removing arXiv timestamp")
        basename = os.path.splitext(input_file)[0]
        uncompress_file = basename + "_uncompress.pdf"

        status = subprocess.call(
            [
                self.pdftk_path,
                input_file,
                "output",
                uncompress_file,
                "uncompress",
            ]
        )
        if not status == 0:
            raise CalledProcessError(
                "pdftk failed to uncompress the PDF file."
            )

        with open(uncompress_file, "rb") as fid:
            data = fid.read()
            # Remove the text element
            data = re.sub(b"\(" + DEARXIV_TEXT_REGEX + b"\)Tj", b"()Tj", data)
            # Remove the URL element
            data = re.sub(
                b"<<\\n\/URI \(http://arxiv\.org/abs/\d{4}\.\d{4,5}v\d+\)\\n\/S /URI\\n>>\\n",
                b"",
                data,
            )

        removed_file = basename + "_removed.pdf"
        with open(removed_file, "wb") as oid:
            oid.write(data)

        output_file = basename + "_dearxiv.pdf"
        status = subprocess.call(
            [self.pdftk_path, removed_file, "output", output_file, "compress"]
        )
        if not status == 0:
            raise CalledProcessError("pdftk failed to compress the PDF file.")

        return output_file
