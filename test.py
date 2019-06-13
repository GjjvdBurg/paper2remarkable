#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "G.J.J. van den Burg"

"""Tests"""

import unittest
import tempfile
import hashlib
import shutil
import os

from arxiv2remarkable import (
    ArxivProvider,
    PMCProvider,
    ACMProvider,
    OpenReviewProvider,
    LocalFileProvider,
    PdfUrlProvider,
)


def md5sum(filename):
    blocksize = 65536
    hasher = hashlib.md5()
    with open(filename, "rb") as fid:
        buf = fid.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fid.read(blocksize)
    return hasher.hexdigest()


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_dir = os.getcwd()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_arxiv(self):
        prov = ArxivProvider(upload=False)
        url = "https://arxiv.org/abs/1811.11242v1"
        exp_filename = "Burg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))
        fsize = os.path.getsize(filename)
        self.assertTrue(1054082 < fsize <= 1056082)

    def test_pmc(self):
        prov = PMCProvider(upload=False)
        url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3474301/"
        exp_filename = (
            "Hoogenboom_Manske_-_How_to_Write_a_Scientific_Article_2012.pdf"
        )
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))
        fsize = os.path.getsize(filename)
        self.assertTrue(376640 < fsize <= 378640)

    def test_acm(self):
        prov = ACMProvider(upload=False)
        url = "https://dl.acm.org/citation.cfm?id=3300356"
        exp_filename = "Muller_et_al_-_How_Data_Science_Workers_Work_With_Data_Discovery_Capture_Curation_Design_Creation_2019.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))
        fsize = os.path.getsize(filename)
        self.assertTrue(1691444 < fsize <= 1693444)

    def test_openreview(self):
        prov = OpenReviewProvider(upload=False)
        url = "https://openreview.net/forum?id=S1x4ghC9tQ"
        exp_filename = "Gregor_et_al_-_Temporal_Difference_Variational_Auto-Encoder_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))
        fsize = os.path.getsize(filename)
        self.assertTrue(1110316 < fsize <= 1112316)

    def test_local(self):
        local_filename = "test.pdf"
        with open(local_filename, "w") as fp:
            fp.write(
                "%PDF-1.1\n%¥±ë\n\n1 0 obj\n  << /Type /Catalog\n     /Pages 2 0 R\n  >>\nendobj\n\n2 0 obj\n  << /Type /Pages\n     /Kids [3 0 R]\n     /Count 1\n     /MediaBox [0 0 300 144]\n  >>\nendobj\n\n3 0 obj\n  <<  /Type /Page\n      /Parent 2 0 R\n      /Resources\n       << /Font\n           << /F1\n               << /Type /Font\n                  /Subtype /Type1\n                  /BaseFont /Times-Roman\n               >>\n           >>\n       >>\n      /Contents 4 0 R\n  >>\nendobj\n\n4 0 obj\n  << /Length 55 >>\nstream\n  BT\n    /F1 18 Tf\n    0 0 Td\n    (Hello World) Tj\n  ET\nendstream\nendobj\n\nxref\n0 5\n0000000000 65535 f \n0000000018 00000 n \n0000000077 00000 n \n0000000178 00000 n \n0000000457 00000 n \ntrailer\n  <<  /Root 1 0 R\n      /Size 5\n  >>\nstartxref\n565\n%%EOF"
            )
        prov = LocalFileProvider(upload=False)
        filename = prov.run(local_filename)
        self.assertEqual("test_.pdf", os.path.basename(filename))
        fsize = os.path.getsize(filename)
        self.assertTrue(5843 < fsize <= 7843)

    def test_pdfurl(self):
        prov = PdfUrlProvider(upload=False)
        url = "http://www.jmlr.org/papers/volume17/14-526/14-526.pdf"
        filename = prov.run(url, filename="test.pdf")
        self.assertEqual("test.pdf", os.path.basename(filename))
        fsize = os.path.getsize(filename)
        self.assertTrue(1828169 < fsize <= 1830169)

if __name__ == "__main__":
    unittest.main()
