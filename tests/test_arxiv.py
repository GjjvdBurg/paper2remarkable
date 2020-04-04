#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for arXiv provider

This file is part of paper2remarkable.

"""

import re
import unittest

from paper2remarkable.providers.arxiv import DEARXIV_TEXT_REGEX


class TestArxiv(unittest.TestCase):
    def test_text_regex_1(self):
        key = b"arXiv:1908.03213v1 [astro.HE] 8 Aug 2019"
        m = re.fullmatch(DEARXIV_TEXT_REGEX, key)
        self.assertIsNotNone(m)

    def test_text_regex_2(self):
        key = b"arXiv:1908.03213v1 [astro-ph.HE] 8 Aug 2019"
        m = re.fullmatch(DEARXIV_TEXT_REGEX, key)
        self.assertIsNotNone(m)


if __name__ == "__main__":
    unittest.main()
