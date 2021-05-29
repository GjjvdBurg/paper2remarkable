#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

from paper2remarkable.exceptions import NoPDFToolError

from paper2remarkable.utils import chdir
from paper2remarkable.utils import check_pdftool


class TestUtils(unittest.TestCase):
    def test_check_pdftool(self):
        # Needs a system with both pdftk and qpdf available
        self.assertEqual(check_pdftool("pdftk", "qpdf"), "pdftk")
        self.assertEqual(check_pdftool("pdftk_xyz", "qpdf"), "qpdf")
        self.assertEqual(check_pdftool("pdftk", "qpdf_xyz"), "pdftk")
        with self.assertRaises(NoPDFToolError):
            check_pdftool("pdftk_xyz", "qpdf_xyz")

    def test_chdir_1(self):
        start_dir = os.getcwd()
        tmpdir1 = tempfile.mkdtemp(prefix="p2r_test_chdir_")
        with chdir(tmpdir1):
            pwd = os.getcwd()
        self.assertEqual(pwd, tmpdir1)
        self.assertEqual(start_dir, os.getcwd())

    def test_chdir_2(self):
        start_dir = os.getcwd()
        tmpdir1 = tempfile.mkdtemp(prefix="p2r_test_chdir_")
        with self.assertRaises(ValueError):
            with chdir(tmpdir1):
                pwd = os.getcwd()
                raise ValueError
        self.assertEqual(pwd, tmpdir1)
        self.assertEqual(start_dir, os.getcwd())


if __name__ == "__main__":
    unittest.main()
