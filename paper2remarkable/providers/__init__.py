# -*- coding: utf-8 -*-

from .acm import ACM
from .arxiv import Arxiv
from .citeseerx import CiteSeerX
from .local import LocalFile
from .neurips import NeurIPS
from .openreview import OpenReview
from .pdf_url import PdfUrl
from .pmlr import PMLR
from .pubmed import PubMed
from .springer import Springer
from .tandfonline import TandFOnline

# NOTE: Order matters here, PdfUrl should be last
providers = [
    ACM,
    Arxiv,
    CiteSeerX,
    NeurIPS,
    OpenReview,
    PMLR,
    PubMed,
    Springer,
    TandFOnline,
    LocalFile,
    PdfUrl,
]
