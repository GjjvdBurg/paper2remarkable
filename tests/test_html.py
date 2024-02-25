#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Additional tests for the HTML provider

This file is part of paper2remarkable.

"""

import os
import unittest

import pdfplumber

from paper2remarkable.providers.html import HTML
from paper2remarkable.providers.html import make_readable
from paper2remarkable.utils import get_page_with_retry


class TestHTML(unittest.TestCase):
    @unittest.skip("Broken test (other url needed)")
    def test_experimental_fix_lazy_loading(self):
        # 2021-05-11 NOTE: This is the only URL I know where the experimental
        # lazy loading fix was useful. It no longer works because Readability
        # strips out the images for this site. If anyone knows of a test case
        # where the experimental fix makes a difference, let me know.
        url = "https://www.seriouseats.com/2015/01/tea-for-everyone.html"
        prov = HTML(upload=False, experimental=True)
        page = get_page_with_retry(url, return_text=True)
        title, article = make_readable(page)
        html_article = prov.preprocess_html(url, title, article)
        expected_image = "https://www.seriouseats.com/images/2015/01/20150118-tea-max-falkowitz-3.jpg"
        self.assertIn(expected_image, html_article)

    def test_custom_css(self):
        test_css = """
        @page { size: 702px 936px; margin: 1in; }
        img { display: block; margin: 0 auto; text-align: center; max-width: 70%; max-height: 300px; }
        h1,h2,h3 { font-family: 'Montserrat'; }
        p, li { font-size: 12pt; line-height: 2; font-family: 'Montserrat'; text-align: left; }
        """

        test_font_urls = [
            "https://fonts.googleapis.com/css2?family=Montserrat&display=swap"
        ]

        url = "https://hbr.org/2019/11/getting-your-team-to-do-more-than-meet-deadlines"
        prov = HTML(upload=False, css=test_css, font_urls=test_font_urls)
        filename = prov.run(url)
        with pdfplumber.open(filename) as pdf:
            self.assertEqual(9, len(pdf.pages))

        os.unlink(filename)


if __name__ == "__main__":
    unittest.main()
