#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Additional tests for the HTML provider

This file is part of paper2remarkable.

"""

import unittest

from paper2remarkable.providers.html import HTML
from paper2remarkable.providers.html import make_readable
from paper2remarkable.utils import get_page_with_retry


class TestHTML(unittest.TestCase):
    def test_experimental_fix_lazy_loading(self):
        url = "https://www.seriouseats.com/2015/01/tea-for-everyone.html"
        prov = HTML(upload=False, experimental=True)
        page = get_page_with_retry(url, return_text=True)
        title, article = make_readable(page)
        html_article = prov.preprocess_html(url, title, article)
        expected_image = "https://www.seriouseats.com/images/2015/01/20150118-tea-max-falkowitz-3.jpg"
        self.assertIn(expected_image, html_article)


if __name__ == "__main__":
    unittest.main()
