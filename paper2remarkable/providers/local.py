# -*- coding: utf-8 -*-

"""Provider for local files

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2019, G.J.J. van den Burg

"""

import os
import shutil

from . import Provider


class LocalFile(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(src):
        return os.path.exists(src)

    def retrieve_pdf(self, src, filename):
        source = os.path.join(self.initial_dir, src)
        shutil.copy(source, filename)

    def get_paper_info(self, src):
        return {"filename": src}

    def create_filename(self, info, filename=None):
        if not filename is None:
            return filename
        return os.path.basename(info["filename"])
