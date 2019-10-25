# -*- coding: utf-8 -*-

from .arxiv import Arxiv
from .pubmed import PubMed
from .acm import ACM
from .openreview import OpenReview
from .springer import Springer
from .local import LocalFile
from .pdf_url import PdfUrl
from .pmlr import PMLR

# NOTE: Order matters here, PdfUrl should be last
providers = [Arxiv, PubMed, ACM, OpenReview, Springer, PMLR, LocalFile, PdfUrl]
