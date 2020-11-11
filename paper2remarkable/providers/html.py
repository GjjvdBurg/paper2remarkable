# -*- coding: utf-8 -*-

"""Provider for HTML documents

This provider is a little bit special, in that it isn't simply pulling an 
academic paper from a site, but instead aims to pull a HTML article.

Author: G.J.J. van den Burg
License: See LICENSE file.
Copyright: 2020, G.J.J. van den Burg

"""

import html2text
import markdown
import re
import readability
import titlecase
import unidecode
import urllib
import weasyprint
import weasyprint.fonts

from ._base import Provider
from ._info import Informer

from ..utils import (
    clean_string,
    get_page_with_retry,
    get_content_type_with_retry,
)
from ..log import Logger

logger = Logger()

CSS = """
@import url('https://fonts.googleapis.com/css?family=EB+Garamond|Noto+Serif|Inconsolata&display=swap');
@page { size: 702px 936px; margin: 1in; }
a { color: black; }
img { display: block; margin: 0 auto; text-align: center; max-width: 70%; max-height: 300px; }
p, li { font-size: 10pt; font-family: 'EB Garamond'; hyphens: auto; text-align: justify; }
h1,h2,h3 { font-family: 'Noto Serif'; }
h1 { font-size: 26px; }
h2 { font-size: 18px; }
h3 { font-size: 14px; }
blockquote { font-style: italic; }
pre { font-family: 'Inconsolata'; padding-left: 2.5%; background: #efefef; }
code { font-family: 'Inconsolata'; font-size: .7rem; background: #efefef; }
"""


def url_fetcher(url):
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("file:///"):
        url = "https:" + url[len("file:/") :]
    return weasyprint.default_url_fetcher(url)


def make_readable(request_html):
    """Use an extraction method to get the main article html

    This function checks if ReadabiliPy is installed with NodeJS support, as
    that generally yields better results. If that is not available, it falls
    back on readability.
    """

    have_readabilipy_js = False
    try:
        import readabilipy

        have_readabilipy_js = readabilipy.simple_json.have_node()
    except ImportError:
        pass

    if have_readabilipy_js:
        logger.info("Converting HTML using Readability.js")
        article = readabilipy.simple_json_from_html_string(
            request_html, use_readability=True
        )
        title = article["title"]
        raw_html = article["content"]
    else:
        logger.info("Converting HTML using readability")
        doc = readability.Document(request_html)
        title = doc.title()
        raw_html = doc.summary(html_partial=True)
    return title, raw_html


class ImgProcessor(markdown.treeprocessors.Treeprocessor):
    def __init__(self, base_url, *args, **kwargs):
        self._base_url = base_url
        super().__init__(*args, **kwargs)

    def run(self, root):
        """ Ensure all img src urls are absolute """
        for img in root.iter("img"):
            img.attrib["src"] = urllib.parse.urljoin(
                self._base_url, img.attrib["src"]
            )
            img.attrib["src"] = img.attrib["src"].rstrip("/")


class HTMLInformer(Informer):
    def __init__(self):
        super().__init__()
        self._cached_title = None
        self._cached_article = None

    def get_filename(self, abs_url):
        request_html = get_page_with_retry(abs_url, return_text=True)
        title, article = make_readable(request_html)

        self._cached_title = title
        self._cached_article = article

        # Clean the title and make it titlecase
        title = clean_string(title)
        title = titlecase.titlecase(title)
        title = title.replace(" ", "_")
        title = clean_string(title)
        name = title.strip("_") + ".pdf"
        name = unidecode.unidecode(name)
        logger.info("Created filename: %s" % name)
        return name


class HTML(Provider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.informer = HTMLInformer()

    def get_abs_pdf_urls(self, url):
        return url, url

    def fix_lazy_loading(self, article):
        if not self.experimental:
            return article

        # This attempts to fix sites where the image src element points to a
        # placeholder and the data-src attribute contains the url to the actual
        # image.
        regex = '<img src="(?P<src>.*?)" (?P<rest1>.*) data-src="(?P<datasrc>.*?)" (?P<rest2>.*?)>'
        sub = '<img src="\g<datasrc>" \g<rest1> \g<rest2>>'

        article, nsub = re.subn(regex, sub, article, flags=re.MULTILINE)
        if nsub:
            logger.info(
                f"[experimental] Attempted to fix lazy image loading ({nsub} times). "
                "Please report bad results."
            )
        return article

    def preprocess_html(self, pdf_url, title, article):
        article = self.fix_lazy_loading(article)

        h2t = html2text.HTML2Text()
        h2t.wrap_links = False
        text = h2t.handle(article)

        # Add the title back to the document
        article = "# {title}\n\n{text}".format(title=title, text=text)

        # Convert to html, fixing relative image urls.
        md = markdown.Markdown()
        md.treeprocessors.register(ImgProcessor(pdf_url), "img", 10)
        html_article = md.convert(article)
        return html_article

    def retrieve_pdf(self, pdf_url, filename):
        """Turn the HTML article in a clean pdf file

        This function takes the following steps:

        1. Pull the HTML page using requests, if not done in Informer
        2. Extract the article part of the page using readability/readabiliPy
        3. Convert the article HTML to markdown using html2text
        4. Convert the markdown back to HTML (done to sanitize the HTML)
        4. Convert the HTML to PDF, pulling in images where needed
        5. Save the PDF to the specified filename.
        """
        if self.informer._cached_title and self.informer._cached_article:
            title = self.informer._cached_title
            article = self.informer._cached_article
        else:
            request_html = get_page_with_retry(pdf_url, return_text=True)
            title, article = make_readable(request_html)

        html_article = self.preprocess_html(pdf_url, title, article)

        if self.debug:
            with open("./paper.html", "w") as fp:
                fp.write(html_article)

        font_config = weasyprint.fonts.FontConfiguration()
        html = weasyprint.HTML(string=html_article, url_fetcher=url_fetcher)
        css = weasyprint.CSS(string=CSS, font_config=font_config)

        html.write_pdf(filename, stylesheets=[css], font_config=font_config)

    def validate(src):
        # first check if it is a valid url
        parsed = urllib.parse.urlparse(src)
        if not all([parsed.scheme, parsed.netloc, parsed.path]):
            return False
        # next, get the header and check the content type
        ct = get_content_type_with_retry(src)
        if ct is None:
            return False
        return ct.startswith("text/html")
