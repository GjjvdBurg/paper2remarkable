#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the PDF operations"""

import os
import shutil
import tempfile
import unittest

from _constants import TEST_FILE
from pikepdf import Pdf

from paper2remarkable.providers.local import LocalFile


class PdfOpsTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp(prefix="p2r_test_blank_")

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def test_blank_pages(self):
        local_filename = os.path.join(self._tmpdir, "test_blank.pdf")
        with open(local_filename, "w") as fp:
            fp.write(TEST_FILE)
        prov = LocalFile(upload=False, blank=True)
        out_filename = os.path.join(self._tmpdir, "test_blank1.pdf")
        filename = prov.run(local_filename, filename=out_filename)
        pdf = Pdf.open(filename)
        self.assertEqual(len(pdf.pages), 2)


if __name__ == "__main__":
    unittest.main()
