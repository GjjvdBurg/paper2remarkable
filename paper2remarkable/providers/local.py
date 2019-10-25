# -*- coding: utf-8 -*-

"""Provider for local files

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import os
import shutil

from ._base import Provider
from ._info import Informer


class LocalFileInformer(Informer):
    def get_filename(self, abs_url):
        return os.path.basename(abs_url)


class LocalFile(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = LocalFileInformer()

    def get_abs_pdf_urls(self, url):
        # The 'url' is the path to the local file. We use this as abs_url and
        # pdf_url.
        return url, url

    def validate(src):
        return os.path.exists(src)

    def retrieve_pdf(self, pdf_url, filename):
        source = os.path.join(self.initial_dir, pdf_url)
        shutil.copy(source, filename)
