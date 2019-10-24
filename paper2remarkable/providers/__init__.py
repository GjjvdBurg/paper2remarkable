# -*- coding: utf-8 -*-

from .arxiv import Arxiv
from .pubmed import Pubmed
from .acm import ACM
from .openreview import OpenReview
from .springer import Springer
from .local import LocalFile
from .pdf_url import PdfUrl

providers = [Arxiv, Pubmed, ACM, OpenReview, Springer, LocalFile, PdfUrl]
