# -*- coding: utf-8 -*-

"""Exceptions for paper2remarkable

"""

from . import GITHUB_URL

from subprocess import CalledProcessError

GH_MSG = "\n\nIf you think this might be a bug, please raise an issue on GitHub at: {url}".format(
    url=GITHUB_URL
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

    def __init__(self, provider):
        self.provider = provider

    def __str__(self):
        msg = "ERROR: Filename must be given with the {provider} provider (hint: use --filename)".format(
            provider=self.provider
        )
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


class _CalledProcessError(CalledProcessError):
    """Exception raised when subprocesses fail.

    We subclass the CalledProcessError so we can add our custom error message.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        parent = super().__str__()
        msg = parent + GH_MSG
        return msg
