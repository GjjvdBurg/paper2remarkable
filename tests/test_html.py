#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Additional tests for the HTML provider

This file is part of paper2remarkable.

"""

import os
import pdfplumber
import tempfile
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

        tmpfd, tempfname_css = tempfile.mkstemp(prefix="p2r_", suffix=".css")
        with os.fdopen(tmpfd, "w") as fp:
            fp.write(test_css)

        tmpfd, tempfname_urls = tempfile.mkstemp(prefix="p2r_", suffix=".txt")
        with os.fdopen(tmpfd, "w") as fp:
            fp.write("\n".join(test_font_urls))

        url = "https://hbr.org/2019/11/getting-your-team-to-do-more-than-meet-deadlines"
        prov = HTML(
            upload=False, css_path=tempfname_css, font_urls_path=tempfname_urls
        )
        filename = prov.run(url)
        with pdfplumber.open(filename) as pdf:
            self.assertEqual(8, len(pdf.pages))

        os.unlink(tempfname_css)
        os.unlink(tempfname_urls)
        os.unlink(filename)


if __name__ == "__main__":
    unittest.main()
