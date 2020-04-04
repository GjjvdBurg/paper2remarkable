# -*- coding: utf-8 -*-

"""Exceptions for paper2remarkable

"""

from . import GITHUB_URL

GH_MSG = (
    "\n\nIf you think this might be a bug, please raise an issue on "
    "GitHub at:\n{url}\n".format(url=GITHUB_URL)
)


class Error(Exception):
    """Base class for exceptions in p2r."""


class URLResolutionError(Error):
    """Exception raised when the abstract/pdf urls can't be resolved.

    Attributes
    ----------
    provider : str
        Name of the provider where the error occurred

    url : str
        Original url provided

    """

    def __init__(self, provider, url, reason=None):
        self.provider = provider
        self.url = url
        self.reason = None

    def __str__(self):
        msg = "ERROR: Couldn't figure out {provider} URLs from provided url: {url}".format(
            provider=self.provider, url=self.url
        )
        if self.reason:
            msg += "\nReason: {reason}".format(reason=self.reason)
        msg += GH_MSG
        return msg


class FilenameMissingError(Error):
    """Exception raised for providers that need a filename to be provided"""

    def __init__(self, provider, url, reason=None):
        self.provider = provider
        self.url = url
        self.reason = reason

    def __str__(self):
        msg = "ERROR: Couldn't determine a filename from {url} for provider {provider}".format(
            provider=self.provider, url=self.url
        )
        if self.reason:
            msg += "\nReason: {reason}".format(reason=self.reason)
        msg += GH_MSG
        return msg


class FileTypeError(Error):
    """Exception raised when we have a mismatch in filetype."""

    def __init__(self, filename, filetype):
        self.filename = filename
        self.filetype = filetype

    def __str__(self):
        msg = "ERROR: File {filename} isn't of type {filetype}.".format(
            filename=self.filename, filetype=self.filetype
        )
        msg += GH_MSG
        return msg


class RemarkableError(Error):
    """Exceptions raised when interacting with the reMarkable fails."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        msg = "ERROR: {message}".format(message=self.message)
        msg += GH_MSG
        return msg


class _CalledProcessError(Error):
    """Exception raised when subprocesses fail.  """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        msg = "ERROR: {message}".format(message=self.message)
        msg += GH_MSG
        return msg


class NoPDFToolError(Error):
    """Exception raised when neither pdftk or qpdf is found."""

    def __init__(self):
        pass

    def __str__(self):
        msg = (
            "ERROR: Neither pdftk or qpdf could be found. Install "
            "either of these or ensure that they can be found using "
            "the --pdftk or --qpdf options."
        )
        msg += GH_MSG
        return msg


class UnidentifiedSourceError(Error):
    """Exception raised when the input is neither a local file nor a url """

    def __str__(self):
        msg = (
            "ERROR: Couldn't figure out what source you mean. If it's a "
            "local file, please make sure it exists."
        )
        msg += GH_MSG
        return msg


class InvalidURLError(Error):
    """Exception raised when no provider can handle a url source """

    def __str__(self):
        msg = (
            "ERROR: Input URL is not valid, no provider can handle "
            "this source."
        )
        msg += GH_MSG
        return msg
