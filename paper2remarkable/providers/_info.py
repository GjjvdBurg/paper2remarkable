# -*- coding: utf-8 -*-

"""Functionality for retrieving paper info
"""

import titlecase
import unidecode
import bs4

from ..utils import clean_string, get_page_with_retry
from ..log import Logger

logger = Logger()


class Informer:
    """Base class for the informers.

    The "informer" class is used to retrieve the title, authors, and year of
    publication of the provided paper.

    This base class provides the main functionality, but because various
    outlets use different conventions to embed author, title, and publication
    year information, we expect that individual providers will subclass this
    class and overwrite some of the methods.
    """

    meta_author_key = "citation_author"
    meta_title_key = "citation_title"
    meta_date_key = "citation_date"

    def __init__(self, title=None, authors=None, year=None):
        self.title = title
        self.authors = authors or []
        self.year = year

    def get_filename(self, abs_url):
        """Generate nice filename using the paper information

        The provided url must be to a HTMl page where this information can be
        found, not to the PDF file itself.
        """
        logger.info("Generating output filename")

        # Retrieve the paper information
        self.get_info(abs_url)

        # we assume that the list of authors is surname only.
        if len(self.authors) > 3:
            authors = self.authors[0] + "_et_al"
        else:
            authors = "_".join(self.authors)
        authors = authors.replace(" ", "_")
        authors = clean_string(authors)

        # Clean the title and make it titlecase
        title = clean_string(self.title)
        title = titlecase.titlecase(title)
        title = title.replace(" ", "_")
        title = clean_string(title)

        year = str(self.year)

        name = authors + "_-_" + title + "_" + year + ".pdf"
        name = unidecode.unidecode(name)
        logger.info("Created filename: %s" % name)
        return name

    def get_info(self, url):
        logger.info("Getting paper info")
        page = get_page_with_retry(url)
        soup = bs4.BeautifulSoup(page, "html.parser")
        self.authors = self.authors or self.get_authors(soup)
        self.title = self.title or self.get_title(soup)
        self.year = self.year or self.get_year(soup)

    ## Title

    def get_title(self, soup):
        meta = soup.find_all("meta", {"name": self.meta_title_key})
        if not meta:
            logger.warning(
                "Couldn't determine title information, maybe provide the desired filename using '--filename'?"
            )
            return ""
        return meta[0]["content"]

    ## Authors

    def _format_authors(self, soup_authors, sep=",", idx=0, op=None):
        op = (lambda x: x) if op is None else op
        # format the author list retrieved by bs4
        return [x.strip().split(sep)[idx].strip() for x in op(soup_authors)]

    def get_authors(self, soup):
        meta = soup.find_all("meta", {"name": self.meta_author_key})
        if not meta:
            logger.warning(
                "Couldn't determine author information, maybe provide the desired filename using '--filename'?"
            )
            return ""
        authors = [x["content"] for x in meta]
        return self._format_authors(authors)

    ## Year

    def _format_year(self, soup_date):
        return soup_date.split("/")[0]

    def get_year(self, soup):
        """ Retrieve the contents of the meta_date_key field and format it """
        meta = soup.find_all("meta", {"name": self.meta_date_key})
        if not meta:
            return ""
        date = meta[0]["content"]
        return self._format_year(date)
