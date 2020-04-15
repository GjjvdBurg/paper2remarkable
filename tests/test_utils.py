#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from paper2remarkable.exceptions import NoPDFToolError
from paper2remarkable.utils import check_pdftool


class TestUtils(unittest.TestCase):
    def test_check_pdftool(self):
        # Needs a system with both pdftk and qpdf available
        self.assertEqual(check_pdftool("pdftk", "qpdf"), "pdftk")
        self.assertEqual(check_pdftool("pdftk_xyz", "qpdf"), "qpdf")
        self.assertEqual(check_pdftool("pdftk", "qpdf_xyz"), "pdftk")
        with self.assertRaises(NoPDFToolError):
            check_pdftool("pdftk_xyz", "qpdf_xyz")


if __name__ == "__main__":
    unittest.main()
