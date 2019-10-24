# -*- coding: utf-8 -*-

from .arxiv import Arxiv
from .pubmed import PubMed
from .acm import ACM
from .openreview import OpenReview
from .springer import Springer
from .local import LocalFile
from .pdf_url import PdfUrl

providers = [Arxiv, PubMed, ACM, OpenReview, Springer, LocalFile, PdfUrl]
