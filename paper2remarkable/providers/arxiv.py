# -*- coding: utf-8 -*-

"""Provider for arxiv.org

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import os
import re

from ._info import Informer
from ._base import Provider
from ..exceptions import URLResolutionError
from ..log import Logger

logger = Logger()

DEARXIV_TEXT_REGEX = b"ar(x|X)iv:(\d{4}\.|[\w\-]+\/)\d+v\d+(\s+\[[\w\-]+\.[\w\-]+\])?\s+\d{1,2}\s\w{3}\s\d{4}"
DEARXIV_URI_REGEX = (
    b"https?://ar(x|X)iv\.org\/abs\/([\w\-]+\/\d+|\d{4}\.\d{4,5})v\d+"
)


class ArxivInformer(Informer):
    pass


class Arxiv(Provider):

    re_abs_1 = "https?://arxiv.org/abs/\d{4}\.\d{4,5}(v\d+)?"
    re_pdf_1 = "https?://arxiv.org/pdf/\d{4}\.\d{4,5}(v\d+)?\.pdf"

    re_abs_2 = "https?://arxiv.org/abs/[\w\-]+/\d{7}(v\d+)?"
    re_pdf_2 = "https?://arxiv.org/pdf/[\w\-]+/\d{7}(v\d+)?.pdf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = ArxivInformer()

        # register the dearxiv operation
        self.operations.insert(0, ("dearxiv", self.dearxiv))

    def get_abs_pdf_urls(self, url):
        """Get the pdf and abs url from any given arXiv url """
        if "?" in url:
            url = url[: url.index("?")]
        if re.match(self.re_abs_1, url) or re.match(self.re_abs_2, url):
            abs_url = url
            pdf_url = url.replace("abs", "pdf") + ".pdf"
        elif re.match(self.re_pdf_1, url) or re.match(self.re_pdf_2, url):
            abs_url = url[:-4].replace("pdf", "abs")
            pdf_url = url
        else:
            raise URLResolutionError("arXiv", url)
        return abs_url, pdf_url

    def validate(src):
        """Check if the url is to an arXiv page. """
        return (
            re.match(Arxiv.re_abs_1, src)
            or re.match(Arxiv.re_pdf_1, src)
            or re.match(Arxiv.re_abs_2, src)
            or re.match(Arxiv.re_pdf_2, src)
        )

    def dearxiv(self, input_file):
        """Remove the arXiv timestamp from a pdf"""
        logger.info("Removing arXiv timestamp ... ", end="")
        basename = os.path.splitext(input_file)[0]

        recoded_file = basename + "_rewrite.pdf"
        self.rewrite_pdf(input_file, recoded_file)

        uncompress_file = basename + "_uncompress.pdf"
        self.uncompress_pdf(recoded_file, uncompress_file)

        new_data = []
        current_obj = []
        replaced_arXiv = False
        char_count = skip_n = startxref = 0
        xref = {}

        with open(uncompress_file, "rb") as fp:
            for line in fp:
                if skip_n:
                    # Skip a line
                    skip_n -= 1
                    continue

                if line.endswith(b" obj\n") or line.endswith(b" obj \n"):
                    # Start a new object. Add it to the current object and
                    # record its position for the xref table.
                    current_obj.append(line)
                    objid = int(line.split(b" ")[0])
                    xref[objid] = char_count
                elif current_obj and (
                    line.startswith(b"endobj")
                    and not line.startswith(b"endobj xref")
                ):
                    # End the current object. If needed, replace the arXiv
                    # stamp in the block (done only once). Reset current
                    # object.
                    current_obj.append(line)
                    block = b"".join(current_obj)
                    # remove the text
                    block, n_subs1 = re.subn(
                        b"\(" + DEARXIV_TEXT_REGEX + b"\)Tj",
                        b"()Tj",
                        block,
                    )
                    # remove the url (type 1)
                    block, n_subs2 = re.subn(
                        b"<<\n\/URI \("
                        + DEARXIV_URI_REGEX
                        + b"\)\n\/S /URI\n>>\n",
                        b"",
                        block,
                    )
                    # remove the url (type 2, i.e. Jackson arXiv 0309285v2)
                    block, n_subs3 = re.subn(
                        b"<<\n\/S \/URI\n"
                        + b"/URI \("
                        + DEARXIV_URI_REGEX
                        + b"\)\n>>\n",
                        b"",
                        block,
                    )

                    if n_subs1 or n_subs2:
                        # fix the length of the object stream
                        block = fix_stream_length(block)
                        replaced_arXiv = True
                    new_data.append(block)
                    char_count += len(block)
                    current_obj = []
                elif line in [b"xref\n", b"endobj xref\n"]:
                    if b"endobj" in line and current_obj:
                        current_obj.append(b"endobj\n")
                        block = b"".join(current_obj)
                        new_data.append(block)
                        char_count += len(block)
                        current_obj = []
                        line = b"xref\n"
                    # We found the xref table, record its position and write it
                    # out using our updated indices.
                    startxref = sum(map(len, new_data))
                    new_data.append(line)
                    new_data.append(b"0 %i\n" % (len(xref) + 1))
                    new_data.append(b"0000000000 65535 f \n")
                    for objid in sorted(xref):
                        new_data.append(b"%010d 00000 n \n" % xref[objid])

                    # skip the appropriate number of lines
                    skip_n = len(xref) + 2
                elif current_obj:
                    # If we're recording an object, simply add the line to it
                    current_obj.append(line)
                elif line == b"startxref\n":
                    # Write out our recorded startxref position, skip the old
                    # position.
                    new_data.append(b"startxref\n%i\n" % startxref)
                    skip_n = 1
                else:
                    # Anything else passes through
                    new_data.append(line)
                    char_count += len(line)

        removed_file = basename + "_removed.pdf"
        with open(removed_file, "wb") as fp:
            fp.write(b"".join(new_data))

        output_file = basename + "_dearxiv.pdf"
        self.compress_pdf(removed_file, output_file)

        logger.append("success" if replaced_arXiv else "none found", "info")

        return output_file


def fix_stream_length(block):
    # This fixes the stream length of a block, which is needed after we have
    # removed the arXiv stamp.
    count = 0
    block = block.split(b"\n")
    do_count = False

    for line in block:
        if line.strip(b" ") in [b"stream", b"endstream"]:
            do_count = not do_count
            continue

        if do_count:
            # +1 for the newline character
            count += len(line) + 1

    new_block = []
    for line in block:
        if b" /Length " in line:
            new_block.append(b"<< /Length %i >>" % count)
        else:
            new_block.append(line)

    return b"\n".join(new_block)
