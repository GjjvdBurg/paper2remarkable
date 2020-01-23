# -*- coding: utf-8 -*-

"""Command line interface

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import argparse
import sys

from . import __version__, GITHUB_URL

from .providers import providers, LocalFile
from .utils import follow_redirects, is_url


def parse_args():
    parser = argparse.ArgumentParser(
        description="Paper2reMarkable version %s" % __version__
    )
    parser.add_argument(
        "-b",
        "--blank",
        help="Add a blank page after every page of the PDF",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--center",
        help="Center the PDF on the page, instead of left align",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="debug mode, doesn't upload to reMarkable",
        action="store_true",
    )
    parser.add_argument(
        "-n",
        "--no-upload",
        help="don't upload to the reMarkable, save the output in current working dir",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--remarkable-path",
        help="directory on reMarkable to put the file (created if missing, default: /)",
        dest="remarkable_dir",
        default="/",
    )
    parser.add_argument(
        "-v", "--verbose", help="be verbose", action="store_true"
    )
    parser.add_argument(
        "--filename",
        help="Filename to use for the file on reMarkable",
        default=None,
    )
    parser.add_argument(
        "--gs", help="path to gs executable (default: gs)", default="gs"
    )
    parser.add_argument(
        "--pdfcrop",
        help="path to pdfcrop executable (default: pdfcrop)",
        default="pdfcrop",
    )
    parser.add_argument(
        "--pdftk",
        help="path to pdftk executable (default: pdftk)",
        default="pdftk",
    )
    parser.add_argument(
        "--rmapi",
        help="path to rmapi executable (default: rmapi)",
        default="rmapi",
    )
    parser.add_argument(
        "input", help="URL to a paper or the path of a local PDF file"
    )
    return parser.parse_args()


def exception(msg):
    print("ERROR: " + msg, file=sys.stderr)
    print("Error occurred. Exiting.", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "If you think this might be a bug, please raise an issue on GitHub: %s"
        % GITHUB_URL
    )
    raise SystemExit(1)


def main():
    args = parse_args()
    cookiejar = None

    if is_url(args.input):
        # input is a url
        url, cookiejar = follow_redirects(args.input)
        provider = next((p for p in providers if p.validate(url)), None)
    elif LocalFile.validate(args.input):
        # input is a local file
        provider = LocalFile
    else:
        # not a proper URL or non-existent file
        exception(
            "Couldn't figure out what source you mean. If it's a "
            "local file, make sure it exists."
        )

    if provider is None:
        exception("Input not valid, no provider can handle this source.")

    prov = provider(
        verbose=args.verbose,
        upload=not args.no_upload,
        debug=args.debug,
        center=args.center,
        blank=args.blank,
        remarkable_dir=args.remarkable_dir,
        rmapi_path=args.rmapi,
        pdfcrop_path=args.pdfcrop,
        pdftk_path=args.pdftk,
        gs_path=args.gs,
        cookiejar=cookiejar,
    )

    prov.run(args.input, filename=args.filename)
