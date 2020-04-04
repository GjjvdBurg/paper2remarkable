#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for command line interface

This file is part of paper2remarkable.

"""

import os
import shutil
import tempfile
import unittest

from paper2remarkable.exceptions import (
    InvalidURLError,
    UnidentifiedSourceError,
)
from paper2remarkable.providers import (
    ACM,
    Arxiv,
    CiteSeerX,
    HTML,
    JMLR,
    LocalFile,
    NBER,
    NeurIPS,
    OpenReview,
    PMLR,
    PdfUrl,
    PubMed,
    Springer,
)
from paper2remarkable.ui import choose_provider


class TestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_dir = os.getcwd()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_choose_provider_1(self):
        tests = [
            (
                Arxiv,
                "https://arxiv.org/abs/1811.11242v1",
                "https://arxiv.org/abs/1811.11242v1",
            ),
            (
                Arxiv,
                "http://arxiv.org/abs/arXiv:1908.03213",
                "https://arxiv.org/abs/1908.03213",
            ),
            (
                Arxiv,
                "https://arxiv.org/abs/math/0309285",
                "https://arxiv.org/abs/math/0309285",
            ),
            (
                Arxiv,
                "https://arxiv.org/pdf/physics/0605197v1.pdf",
                "https://arxiv.org/pdf/physics/0605197v1.pdf",
            ),
            (
                PubMed,
                "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3474301/",
                "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3474301/",
            ),
            (
                ACM,
                "https://dl.acm.org/citation.cfm?id=3025626",
                "https://dl.acm.org/doi/10.1145/3025453.3025626",
            ),
            (
                ACM,
                "https://dl.acm.org/doi/pdf/10.1145/3219819.3220081?download=true",
                "https://dl.acm.org/doi/pdf/10.1145/3219819.3220081?download=true&",
            ),
            (
                OpenReview,
                "http://openreview.net/forum?id=S1x4ghC9tQ",
                "https://openreview.net/forum?id=S1x4ghC9tQ",
            ),
            (
                Springer,
                "https://link.springer.com/article/10.1007/s10618-019-00631-5",
                "https://link.springer.com/article/10.1007/s10618-019-00631-5",
            ),
            (
                PdfUrl,
                "https://gertjanvandenburg.com/papers/VandenBurg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2019.pdf",
                "https://gertjanvandenburg.com/papers/VandenBurg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2019.pdf",
            ),
            (
                JMLR,
                "http://www.jmlr.org/papers/volume17/14-526/14-526.pdf",
                "http://www.jmlr.org/papers/volume17/14-526/14-526.pdf",
            ),
            (
                JMLR,
                "http://www.jmlr.org/papers/v10/xu09a.html",
                "http://www.jmlr.org/papers/v10/xu09a.html",
            ),
            (
                PMLR,
                "http://proceedings.mlr.press/v97/behrmann19a.html",
                "http://proceedings.mlr.press/v97/behrmann19a.html",
            ),
            (
                PMLR,
                "http://proceedings.mlr.press/v15/maaten11b/maaten11b.pdf",
                "http://proceedings.mlr.press/v15/maaten11b/maaten11b.pdf",
            ),
            (
                PMLR,
                "http://proceedings.mlr.press/v48/melnyk16.pdf",
                "http://proceedings.mlr.press/v48/melnyk16.pdf",
            ),
            (
                PMLR,
                "http://proceedings.mlr.press/v48/zhangf16.html",
                "http://proceedings.mlr.press/v48/zhangf16.html",
            ),
            (
                NBER,
                "https://www.nber.org/papers/w26752",
                "https://www.nber.org/papers/w26752",
            ),
            (
                NBER,
                "https://www.nber.org/papers/w19152.pdf",
                "https://www.nber.org/papers/w19152.pdf",
            ),
            (
                NeurIPS,
                "https://papers.nips.cc/paper/325-leaning-by-combining-memorization-and-gradient-descent.pdf",
                "https://papers.nips.cc/paper/325-leaning-by-combining-memorization-and-gradient-descent.pdf",
            ),
            (
                NeurIPS,
                "https://papers.nips.cc/paper/7796-middle-out-decoding",
                "https://papers.nips.cc/paper/7796-middle-out-decoding",
            ),
            (
                CiteSeerX,
                "http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.89.6548",
                "http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.89.6548",
            ),
            (
                CiteSeerX,
                "http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.123.7607&rep=rep1&type=pdf",
                "http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.123.7607&rep=rep1&type=pdf",
            ),
            (
                HTML,
                "https://hbr.org/2019/11/getting-your-team-to-do-more-than-meet-deadlines",
                "https://hbr.org/2019/11/getting-your-team-to-do-more-than-meet-deadlines",
            ),
            (
                HTML,
                "https://www.nature.com/articles/d41586-020-00176-4",
                "https://www.nature.com/articles/d41586-020-00176-4",
            ),
        ]
        for exp_prov, url, exp_url in tests:
            prov, new_url, jar = choose_provider(url)
            with self.subTest(url=url):
                self.assertEqual(exp_url, new_url)
                self.assertEqual(prov, exp_prov)

    def test_choose_provider_2(self):
        local_filename = "test.pdf"
        with open(local_filename, "w") as fp:
            fp.write(
                "%PDF-1.1\n%¥±ë\n\n1 0 obj\n  << /Type /Catalog\n     /Pages 2 0 R\n  >>\nendobj\n\n2 0 obj\n  << /Type /Pages\n     /Kids [3 0 R]\n     /Count 1\n     /MediaBox [0 0 300 144]\n  >>\nendobj\n\n3 0 obj\n  <<  /Type /Page\n      /Parent 2 0 R\n      /Resources\n       << /Font\n           << /F1\n               << /Type /Font\n                  /Subtype /Type1\n                  /BaseFont /Times-Roman\n               >>\n           >>\n       >>\n      /Contents 4 0 R\n  >>\nendobj\n\n4 0 obj\n  << /Length 55 >>\nstream\n  BT\n    /F1 18 Tf\n    0 0 Td\n    (Hello World) Tj\n  ET\nendstream\nendobj\n\nxref\n0 5\n0000000000 65535 f \n0000000018 00000 n \n0000000077 00000 n \n0000000178 00000 n \n0000000457 00000 n \ntrailer\n  <<  /Root 1 0 R\n      /Size 5\n  >>\nstartxref\n565\n%%EOF"
            )

        prov, new_input, jar = choose_provider(local_filename)
        self.assertEqual(prov, LocalFile)
        self.assertEqual(new_input, local_filename)
        self.assertIsNone(jar)

    def test_choose_provider_3(self):
        local_filename = "/tmp/abcdef.pdf"
        with self.assertRaises(UnidentifiedSourceError):
            choose_provider(local_filename)

    def test_choose_provider_4(self):
        url = "https://raw.githubusercontent.com/GjjvdBurg/paper2remarkable/master/README.md"
        with self.assertRaises(InvalidURLError):
            choose_provider(url)


if __name__ == "__main__":
    unittest.main()
