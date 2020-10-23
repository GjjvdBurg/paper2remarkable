# -*- coding: utf-8 -*-

"""Just a simple logger

Author: G.J.J. van den Burg
License: See LICENSE file.
Copyright: 2019, G.J.J. van den Burg

"""

# NOTE: I know about the logging module, but this was easier because one of the
# dependencies was using that and it became complicated. This one is obviously
# not thread-safe and is very simple.

import datetime
import sys


class Singleton(type):
    # https://stackoverflow.com/q/6760685
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


class Logger(metaclass=Singleton):
    def __init__(self):
        self.enabled = True

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def _log(self, msg, mode, end="\n", add_prefix=True):
        if not self.enabled:
            return
        if not mode in ("info", "warn"):
            raise ValueError("Unknown logging mode: %s" % mode)
        file = sys.stdout if mode == "info" else sys.stderr
        if add_prefix:
            now = datetime.datetime.now()
            nowstr = now.strftime("%Y-%m-%d %H:%M:%S")
            prefix = "%s - %s - " % (nowstr, mode.upper())
        else:
            prefix = ""
        print("%s%s" % (prefix, msg), end=end, file=file)
        file.flush()

    def info(self, msg, end="\n"):
        self._log(msg, "info", end=end)

    def warning(self, msg, end="\n"):
        self._log(msg, "warn", end=end)

    def append(self, msg, mode, end="\n"):
        self._log(msg, mode, end=end, add_prefix=False)
