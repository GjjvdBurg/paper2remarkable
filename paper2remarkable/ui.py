# -*- coding: utf-8 -*-

"""Command line interface

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import argparse
import sys

from . import __version__, GITHUB_URL

from .exceptions import UnidentifiedSourceError, InvalidURLError
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
        "-e",
        "--experimental",
        help="enable experimental features",
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
        "-r",
        "--right",
        help="Right align so the menu doesn't cover it",
        action="store_true",
    )
    parser.add_argument(
        "-k", "--no-crop", help="Don't crop the pdf file", action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose", help="be verbose", action="store_true"
    )
    parser.add_argument(
        "-V",
        "--version",
        help="Show version and exit",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "--filename",
        help="Filename to use for the file on reMarkable",
        action="append",
    )
    parser.add_argument(
        "--gs", help="path to gs executable (default: gs)", default="gs"
    )
    parser.add_argument(
        "--pdftoppm",
        help="path to pdftoppm executable (default: pdftoppm)",
        default="pdftoppm",
    )
    parser.add_argument(
        "--pdftk",
        help="path to pdftk executable (default: pdftk)",
        default="pdftk",
    )
    parser.add_argument(
        "--qpdf",
        help="path to qpdf executable (default: qpdf)",
        default="qpdf",
    )
    parser.add_argument(
        "--rmapi",
        help="path to rmapi executable (default: rmapi)",
        default="rmapi",
    )
    parser.add_argument(
        "input",
        help="One or more URLs to a paper or paths to local PDF files",
        nargs="+",
    )
    return parser.parse_args()


def exception(msg):
    print("ERROR: " + msg, file=sys.stderr)
    print("Error occurred. Exiting.", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "If you think this might be a bug, please raise an issue on GitHub: %s"
        % GITHUB_URL,
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    raise SystemExit(1)


def choose_provider(cli_input):
    """Choose the provider to use for the given source

    This function first tries to check if the input is a local file, by
    checking if the path exists. Next, it checks if the input is a "valid" url
    using a regex test. If it is, the registered provider classes are checked
    to see which provider can handle this url.

    Returns
    -------
    provider : class
        The class of the provider than can handle the source. A subclass of the
        Provider abc.

    new_input : str
        The updated input to the provider. This only has an effect for the url
        providers, where this will be the url after following all redirects.

    cookiejar : dict or requests.RequestsCookieJar
        Cookies picked up when following redirects. These are needed for some
        providers to ensure later requests have the right cookie settings.

    Raises
    ------
    UnidentifiedSourceError
        Raised when the input is neither an existing local file nor a valid url

    InvalidURLError
        Raised when the input *is* a valid url, but no provider can handle it.

    """
    provider = cookiejar = None
    if LocalFile.validate(cli_input):
        # input is a local file
        new_input = cli_input
        provider = LocalFile
    elif is_url(cli_input):
        # input is a url
        new_input, cookiejar = follow_redirects(cli_input)
        provider = next((p for p in providers if p.validate(new_input)), None)
    else:
        # not a proper URL or non-existent file
        raise UnidentifiedSourceError

    if provider is None:
        raise InvalidURLError

    return provider, new_input, cookiejar


def set_excepthook(debug):
    sys_hook = sys.excepthook

    def exception_handler(exception_type, value, traceback):
        if debug:
            sys_hook(exception_type, value, traceback)
        else:
            print(value, file=sys.stderr)

    sys.excepthook = exception_handler


def main():
    args = parse_args()
    set_excepthook(args.debug)

    if args.center and args.right:
        exception("Can't center and right align at the same time!")

    if args.center and args.no_crop:
        exception("Can't center and not crop at the same time!")

    if args.right and args.no_crop:
        exception("Can't right align and not crop at the same time!")

    if args.filename and not len(args.filename) == len(args.input):
        exception(
            "When providing --filename and multiple inputs, their number must match."
        )

    filenames = (
        [None] * len(args.input) if not args.filename else args.filename
    )

    for cli_input, filename in zip(args.input, filenames):
        provider, new_input, cookiejar = choose_provider(cli_input)
        prov = provider(
            verbose=args.verbose,
            upload=not args.no_upload,
            debug=args.debug,
            experimental=args.experimental,
            center=args.center,
            right=args.right,
            blank=args.blank,
            no_crop=args.no_crop,
            remarkable_dir=args.remarkable_dir,
            rmapi_path=args.rmapi,
            pdftoppm_path=args.pdftoppm,
            pdftk_path=args.pdftk,
            qpdf_path=args.qpdf,
            gs_path=args.gs,
            cookiejar=cookiejar,
        )
        prov.run(new_input, filename=filename)
