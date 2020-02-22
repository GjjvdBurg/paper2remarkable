# -*- coding: utf-8 -*-

from .acm import ACM
from .arxiv import Arxiv
from .citeseerx import CiteSeerX
from .html import HTML
from .jmlr import JMLR
from .local import LocalFile
from .nber import NBER
from .neurips import NeurIPS
from .openreview import OpenReview
from .pdf_url import PdfUrl
from .pmlr import PMLR
from .pubmed import PubMed
from .springer import Springer

# NOTE: Order matters here, PdfUrl and HTML should be last
providers = [
    ACM,
    Arxiv,
    CiteSeerX,
    JMLR,
    NBER,
    NeurIPS,
    OpenReview,
    PMLR,
    PubMed,
    Springer,
    LocalFile,
    PdfUrl,
    HTML,
]
