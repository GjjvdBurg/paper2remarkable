#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for command line interface

This file is part of paper2remarkable.

"""

import os
import shutil
import tempfile
import unittest

from paper2remarkable.exceptions import InvalidURLError
from paper2remarkable.exceptions import UnidentifiedSourceError
from paper2remarkable.providers import ACL
from paper2remarkable.providers import ACM
from paper2remarkable.providers import CVF
from paper2remarkable.providers import ECCC
from paper2remarkable.providers import HTML
from paper2remarkable.providers import IACR
from paper2remarkable.providers import JMLR
from paper2remarkable.providers import NBER
from paper2remarkable.providers import PMLR
from paper2remarkable.providers import Arxiv
from paper2remarkable.providers import CiteSeerX
from paper2remarkable.providers import LocalFile
from paper2remarkable.providers import Nature
from paper2remarkable.providers import NeurIPS
from paper2remarkable.providers import OpenReview
from paper2remarkable.providers import PdfUrl
from paper2remarkable.providers import PubMed
from paper2remarkable.providers import Springer
from paper2remarkable.ui import build_argument_parser
from paper2remarkable.ui import choose_provider
from paper2remarkable.ui import merge_options
from paper2remarkable.ui import runner
from paper2remarkable.utils import chdir


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
                "http://arxiv.org/abs/1908.03213",
            ),
            (
                Arxiv,
                "https://arxiv.org/abs/math/0309285",
                "https://arxiv.org/abs/math/0309285",
            ),
            (
                Arxiv,
                "https://arxiv.org/pdf/physics/0605197v1.pdf",
                "http://arxiv.org/pdf/physics/0605197v1",
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
            # ( # Disabled, adds & at the end locally but not on Github
            #    ACM,
            #    "https://dl.acm.org/doi/pdf/10.1145/3219819.3220081?download=true",
            #    "https://dl.acm.org/doi/pdf/10.1145/3219819.3220081?download=true",
            # ),
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
            # (
            #     PdfUrl,
            #     "https://confcats_isif.s3.amazonaws.com/web-files/journals/entries/Nonlinear%20Kalman%20Filters.pdf",
            #     "https://confcats_isif.s3.amazonaws.com/web-files/journals/entries/Nonlinear%20Kalman%20Filters.pdf",
            # ),
            (
                PdfUrl,
                "http://publications.aston.ac.uk/id/eprint/38334/1/5th_Artificial_Neural_Networks.pdf",
                "https://publications.aston.ac.uk/id/eprint/38334/1/5th_Artificial_Neural_Networks.pdf",
            ),
            (
                IACR,
                "https://eprint.iacr.org/1999/011",
                "https://eprint.iacr.org/1999/011",
            ),
            (
                IACR,
                "https://eprint.iacr.org/2021/685.pdf",
                "https://eprint.iacr.org/2021/685.pdf",
            ),
            (
                JMLR,
                "https://www.jmlr.org/papers/volume17/14-526/14-526.pdf",
                "https://www.jmlr.org/papers/volume17/14-526/14-526.pdf",
            ),
            (
                JMLR,
                "https://www.jmlr.org/papers/v10/xu09a.html",
                "https://www.jmlr.org/papers/v10/xu09a.html",
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
                "https://www.nber.org/system/files/working_papers/w19152/w19152.pdf",
            ),
            # ( # disabling; no longer redirected
            #     NeurIPS,
            #     "https://papers.nips.cc/paper/325-leaning-by-combining-memorization-and-gradient-descent.pdf",
            #     "https://proceedings.neurips.cc/paper/1990/file/89f0fd5c927d466d6ec9a21b9ac34ffa-Paper.pdf",
            # ),
            (
                NeurIPS,
                "https://papers.nips.cc/paper/7796-middle-out-decoding",
                "https://papers.nips.cc/paper_files/paper/2018/hash/0c215f194276000be6a6df6528067151-Abstract.html",
            ),
            (
                NeurIPS,
                "http://papers.neurips.cc/paper/7368-on-the-dimensionality-of-word-embedding.pdf",
                "https://proceedings.neurips.cc/paper_files/paper/2018/file/b534ba68236ba543ae44b22bd110a1d6-Paper.pdf",
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
            (
                CVF,
                "https://openaccess.thecvf.com/content_cvpr_2018/html/Cheng_Dual_Skipping_Networks_CVPR_2018_paper.html",
                "https://openaccess.thecvf.com/content_cvpr_2018/html/Cheng_Dual_Skipping_Networks_CVPR_2018_paper.html",
            ),
            (
                Nature,
                "https://www.nature.com/articles/s41599-019-0349-z",
                "https://www.nature.com/articles/s41599-019-0349-z",
            ),
            (
                ACL,
                "https://www.aclweb.org/anthology/2020.sigmorphon-1.29v2.pdf",
                "https://aclanthology.org/2020.sigmorphon-1.29v2.pdf",
            ),
            (
                ECCC,
                "https://eccc.weizmann.ac.il/report/2019/006/",
                "https://eccc.weizmann.ac.il/report/2019/006/",
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

    def test_merge_options_1(self):
        config = None
        source = "/tmp/local.pdf"  # doesn't need to exist

        parser = build_argument_parser()
        args = parser.parse_args([source])

        # empty config and default args
        opts = merge_options(args, config)
        self.assertEqual(opts["core"]["blank"], False)
        self.assertEqual(opts["core"]["crop"], "left")
        self.assertEqual(opts["core"]["experimental"], False)
        self.assertEqual(opts["core"]["upload"], True)
        self.assertEqual(opts["core"]["verbose"], False)
        self.assertEqual(opts["core"]["remarkable_dir"], "/")

        test_sys = lambda s: self.assertEqual(opts["system"][s], s)
        for s in ["gs", "pdftoppm", "pdftk", "qpdf", "rmapi"]:
            with self.subTest(s):
                test_sys(s)

        self.assertIsNone(opts["html"]["css"])
        self.assertIsNone(opts["html"]["font_urls"])

    def test_merge_options_2(self):
        config = None
        source = "/tmp/local.pdf"  # doesn't need to exist

        parser = build_argument_parser()
        args = parser.parse_args(["-v", "-n", source])

        # empty config and default args
        opts = merge_options(args, config)

        self.assertEqual(opts["core"]["blank"], False)
        self.assertEqual(opts["core"]["crop"], "left")
        self.assertEqual(opts["core"]["experimental"], False)
        self.assertEqual(opts["core"]["upload"], False)
        self.assertEqual(opts["core"]["verbose"], True)
        self.assertEqual(opts["core"]["remarkable_dir"], "/")

        test_sys = lambda s: self.assertEqual(opts["system"][s], s)
        for s in ["gs", "pdftoppm", "pdftk", "qpdf", "rmapi"]:
            with self.subTest(s):
                test_sys(s)

        self.assertIsNone(opts["html"]["css"])
        self.assertIsNone(opts["html"]["font_urls"])

    def test_merge_options_3(self):
        source = "/tmp/local.pdf"  # doesn't need to exist

        parser = build_argument_parser()
        args = parser.parse_args(["-v", "-n", "-k", source])
        config = {"core": {"blank": True, "upload": True, "verbose": False}}

        # empty config and default args
        opts = merge_options(args, config)

        self.assertEqual(opts["core"]["blank"], True)
        self.assertEqual(opts["core"]["crop"], "none")
        self.assertEqual(opts["core"]["experimental"], False)
        self.assertEqual(opts["core"]["upload"], False)
        self.assertEqual(opts["core"]["verbose"], True)
        self.assertEqual(opts["core"]["remarkable_dir"], "/")

        test_sys = lambda s: self.assertEqual(opts["system"][s], s)
        for s in ["gs", "pdftoppm", "pdftk", "qpdf", "rmapi"]:
            with self.subTest(s):
                test_sys(s)

        self.assertIsNone(opts["html"]["css"])
        self.assertIsNone(opts["html"]["font_urls"])

    def test_merge_options_4(self):
        source = "/tmp/local.pdf"  # doesn't need to exist

        parser = build_argument_parser()
        args = parser.parse_args(["-n", "-c", source])
        gs_path = "/path/to/gs"
        config = {
            "core": {
                "upload": False,
                "verbose": True,
                "remarkable_dir": "/Tools",
            },
            "system": {"gs": gs_path},
        }

        # empty config and default args
        opts = merge_options(args, config)

        self.assertEqual(opts["core"]["blank"], False)
        self.assertEqual(opts["core"]["crop"], "center")
        self.assertEqual(opts["core"]["experimental"], False)
        self.assertEqual(opts["core"]["upload"], False)
        self.assertEqual(opts["core"]["verbose"], True)
        self.assertEqual(opts["core"]["remarkable_dir"], "/Tools")

        self.assertEqual(opts["system"]["gs"], gs_path)
        test_sys = lambda s: self.assertEqual(opts["system"][s], s)
        for s in ["pdftoppm", "pdftk", "qpdf", "rmapi"]:
            with self.subTest(s):
                test_sys(s)

        self.assertIsNone(opts["html"]["css"])
        self.assertIsNone(opts["html"]["font_urls"])

    def test_merge_options_5(self):
        source = "/tmp/local.pdf"  # doesn't need to exist

        parser = build_argument_parser()
        args = parser.parse_args(["-n", "-p", "/Tools", "-c", source])
        gs_path = "/path/to/gs"
        qpdf_path = "/path/to/qpdf"
        config = {
            "core": {"upload": False, "verbose": True},
            "system": {"gs": gs_path, "qpdf": qpdf_path},
            "html": {
                "css": "Hello, World!\n",
                "font_urls": ["url_1", "url_2"],
            },
        }

        # empty config and default args
        opts = merge_options(args, config)

        self.assertEqual(opts["core"]["blank"], False)
        self.assertEqual(opts["core"]["crop"], "center")
        self.assertEqual(opts["core"]["experimental"], False)
        self.assertEqual(opts["core"]["upload"], False)
        self.assertEqual(opts["core"]["verbose"], True)
        self.assertEqual(opts["core"]["remarkable_dir"], "/Tools")

        self.assertEqual(opts["system"]["gs"], gs_path)
        self.assertEqual(opts["system"]["qpdf"], qpdf_path)
        test_sys = lambda s: self.assertEqual(opts["system"][s], s)
        for s in ["pdftoppm", "pdftk", "rmapi"]:
            with self.subTest(s):
                test_sys(s)

        self.assertEqual(opts["html"]["css"], "Hello, World!\n")
        self.assertEqual(opts["html"]["font_urls"], ["url_1", "url_2"])

    def test_runner_1(self):
        inputs = [
            "https://arxiv.org/abs/1811.11242v1",
        ]
        filenames = [None]
        options = {
            "core": {
                "blank": False,
                "verbose": False,
                "upload": False,
                "experimental": False,
                "crop": "none",
                "remarkable_dir": "/",
            },
            "system": {
                "gs": "gs",
                "pdftoppm": "pdftoppm",
                "pdftk": "pdftk",
                "qpdf": "qpdf",
                "rmapi": "rmapi",
            },
            "html": {"css": None, "font_urls": None},
        }

        test_dir = tempfile.mkdtemp()
        with chdir(test_dir):
            runner(inputs, filenames, options)

        pth = os.path.join(
            test_dir,
            "Burg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2018.pdf",
        )
        self.assertTrue(os.path.exists(pth))

    def test_runner_2(self):
        test_upload = False  # Enable to test uploading to reMarkable

        if test_upload:
            upload = True
            rm_dir = "/p2r_test"
        else:
            upload = False
            rm_dir = "/"

        inputs = [
            "https://arxiv.org/abs/1811.11242v1",
            "https://www.jmlr.org/papers/volume17/14-526/14-526.pdf",
        ]
        filenames = [None, None]
        options = {
            "core": {
                "blank": False,
                "verbose": False,
                "upload": upload,
                "experimental": False,
                "crop": "none",
                "remarkable_dir": rm_dir,
            },
            "system": {
                "gs": "gs",
                "pdftoppm": "pdftoppm",
                "pdftk": "pdftk",
                "qpdf": "qpdf",
                "rmapi": "rmapi",
            },
            "html": {"css": None, "font_urls": None},
        }

        test_dir = tempfile.mkdtemp()
        with chdir(test_dir):
            runner(inputs, filenames, options)

        pth = os.path.join(
            test_dir,
            "Burg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2018.pdf",
        )
        if test_upload:
            self.assertFalse(os.path.exists(pth))
        else:
            self.assertTrue(os.path.exists(pth))

        pth = os.path.join(
            test_dir,
            "Burg_Groenen_-_GenSVM_a_Generalized_Multiclass_Support_Vector_Machine_2016.pdf",
        )
        if test_upload:
            self.assertFalse(os.path.exists(pth))
        else:
            self.assertTrue(os.path.exists(pth))


if __name__ == "__main__":
    unittest.main()
