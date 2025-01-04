# -*- coding: utf-8 -*-

"""Command line interface

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import argparse
import copy
import os
import sys

import validators
import yaml

from . import GITHUB_URL
from . import __version__
from .exceptions import InvalidURLError
from .exceptions import UnidentifiedSourceError
from .providers import LocalFile
from .providers import providers
from .utils import follow_redirects


def build_argument_parser():
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
        help="don't upload to reMarkable, save the output in current directory",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--remarkable-path",
        help="directory on reMarkable to put the file (created if missing, default: /)",
        dest="remarkable_dir",
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
        "-f",
        "--filename",
        help="Filename to use for the file on reMarkable",
        action="append",
    )
    parser.add_argument(
        "--usb-upload",
        help="upload through usb instead of rmapi",
        action="store_true",
    )
    parser.add_argument(
        "--gs", help="path to gs executable (default: gs)", default=None
    )
    parser.add_argument(
        "--pdftoppm",
        help="path to pdftoppm executable (default: pdftoppm)",
        default=None,
    )
    parser.add_argument(
        "--pdftk",
        help="path to pdftk executable (default: pdftk)",
        default=None,
    )
    parser.add_argument(
        "--qpdf",
        help="path to qpdf executable (default: qpdf)",
        default=None,
    )
    parser.add_argument(
        "--rmapi",
        help="path to rmapi executable (default: rmapi)",
        default=None,
    )
    parser.add_argument(
        "--css", help="path to custom CSS file for HTML output", default=None
    )
    parser.add_argument(
        "--font-urls",
        help="path to custom font urls file for HTML output",
        default=None,
    )
    parser.add_argument(
        "-C",
        "--config",
        help="path to config file (default: ~/.paper2remarkable.yml)",
        default=None,
    )
    parser.add_argument(
        "--source",
        choices=["url", "file"],
        help=(
            "Force the source type (url or file) in case of detection failure."
            " This is useful when the input is ambiguous, but be aware that "
            "this does not guarantee successful processing."
        ),
    )
    parser.add_argument(
        "input",
        help="One or more URLs to a paper or paths to local PDF files",
        nargs="+",
    )
    return parser


def parse_args():
    parser = build_argument_parser()
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


def choose_provider(cli_input, source_type=None):
    """Choose the provider to use for the given source

    This function determines the appropriate provider based on the input and the
    optional source_type parameter. If source_type is specified, it overrides
    the automatic detection. Otherwise, it first tries to check if the input is
    a local file by checking if the path exists. Next, it checks if the input is
    a "valid" url using a regex test. If it is, the registered provider classes
    are checked to see which provider can handle this url.

    Parameters
    ----------
    cli_input : str
        The input provided by the user, either a file path or a URL.
    source_type : str, optional
        The type of the source, either "file" or "url". If provided, it overrides
        the automatic detection.

    Returns
    -------
    provider : class
        The class of the provider that can handle the source. A subclass of the
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
        Raised when the input is neither an existing local file nor a valid url,
        and no valid source_type is provided.

    InvalidURLError
        Raised when the input *is* a valid url (or source_type is "url"), but no
        provider can handle it.
    """
    provider = cookiejar = None
    if source_type == "file" or (
        source_type is None and LocalFile.validate(cli_input)
    ):
        # input is a local file or user specified source type is file
        new_input = cli_input
        provider = LocalFile
    elif source_type == "url" or (
        source_type is None and validators.url(cli_input)
    ):
        # input is a url or user specified source type is url
        new_input, cookiejar = follow_redirects(cli_input)
        provider = next((p for p in providers if p.validate(new_input)), None)
    else:
        # not a proper URL or non-existent file
        raise UnidentifiedSourceError

    if provider is None:
        raise InvalidURLError

    return provider, new_input, cookiejar


def load_config(path=None):
    if path is None:
        path = os.path.join(os.path.expanduser("~"), ".paper2remarkable.yml")
    if not os.path.exists(path):
        return None
    with open(path, "r") as fp:
        config = yaml.safe_load(fp)
    return config


def merge_options(args, config=None):
    # command line arguments always overwrite config
    config = {} if config is None else config

    opts = copy.deepcopy(config)
    opts.setdefault("core", {})
    opts.setdefault("system", {})
    opts.setdefault("html", {})

    def set_bool(d, key, value, invert=False):
        if value:
            d[key] = True ^ invert
        elif key not in d:
            d[key] = False ^ invert

    def set_path(d, key, value):
        if value is not None:
            d[key] = value
        elif key not in d:
            d[key] = key

    set_bool(opts["core"], "blank", args.blank)
    set_bool(opts["core"], "verbose", args.verbose)
    set_bool(opts["core"], "upload", args.no_upload, invert=True)
    set_bool(opts["core"], "experimental", args.experimental)
    set_bool(opts["core"], "usb_upload", args.usb_upload)

    if args.center:
        opts["core"]["crop"] = "center"
    elif args.right:
        opts["core"]["crop"] = "right"
    elif args.no_crop:
        opts["core"]["crop"] = "none"
    elif "crop" not in opts["core"]:
        opts["core"]["crop"] = "left"

    if args.remarkable_dir is not None:
        opts["core"]["remarkable_dir"] = args.remarkable_dir
    elif "remarkable_dir" not in opts["core"]:
        opts["core"]["remarkable_dir"] = "/"

    set_path(opts["system"], "gs", args.gs)
    set_path(opts["system"], "pdftoppm", args.pdftoppm)
    set_path(opts["system"], "pdftk", args.pdftk)
    set_path(opts["system"], "qpdf", args.qpdf)
    set_path(opts["system"], "rmapi", args.rmapi)

    if args.css and os.path.exists(args.css):
        with open(args.css, "r") as fp:
            contents = fp.read()
        opts["html"]["css"] = contents
    elif "css" not in opts["html"]:
        opts["html"]["css"] = None

    if args.font_urls and os.path.exists(args.font_urls):
        with open(args.font_urls, "r") as fp:
            urls = [line.strip() for line in fp.readlines()]
        opts["html"]["font_urls"] = urls
    elif "font_urls" not in opts["html"]:
        opts["html"]["font_urls"] = None

    return opts


def set_excepthook(debug):
    sys_hook = sys.excepthook

    def exception_handler(exception_type, value, traceback):
        if debug:
            sys_hook(exception_type, value, traceback)
        else:
            print(value, file=sys.stderr)

    sys.excepthook = exception_handler


def runner(inputs, filenames, options, debug=False):
    if not len(inputs) == len(filenames):
        raise ValueError("Number of inputs and filenames must be the same")
    for cli_input, filename in zip(inputs, filenames):
        provider, new_input, cookiejar = choose_provider(
            cli_input, options["core"].get("source")
        )
        prov = provider(
            verbose=options["core"]["verbose"],
            upload=options["core"]["upload"],
            debug=debug,
            experimental=options["core"]["experimental"],
            crop=options["core"]["crop"],
            blank=options["core"]["blank"],
            remarkable_dir=options["core"]["remarkable_dir"],
            usb_upload=options["core"]["usb_upload"],
            rmapi_path=options["system"]["rmapi"],
            pdftoppm_path=options["system"]["pdftoppm"],
            pdftk_path=options["system"]["pdftk"],
            qpdf_path=options["system"]["qpdf"],
            gs_path=options["system"]["gs"],
            css=options["html"]["css"],
            font_urls=options["html"]["font_urls"],
            cookiejar=cookiejar,
        )
        prov.run(new_input, filename=filename)


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

    config = load_config(path=args.config)
    options = merge_options(args, config=config)

    filenames = (
        [None] * len(args.input) if not args.filename else args.filename
    )

    runner(args.input, filenames, options, debug=args.debug)
