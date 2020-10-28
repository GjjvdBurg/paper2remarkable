# -*- coding: utf-8 -*-

from .acm import ACM
from .arxiv import Arxiv
from .citeseerx import CiteSeerX
from .cvf import CVF
from .html import HTML
from .jmlr import JMLR
from .local import LocalFile
from .nature import Nature
from .nber import NBER
from .neurips import NeurIPS
from .openreview import OpenReview
from .pdf_url import PdfUrl
from .pmlr import PMLR
from .pubmed import PubMed
from .sagepub import SagePub
from .semantic_scholar import SemanticScholar
from .springer import Springer
from .tandfonline import TandFOnline

# NOTE: Order matters here, PdfUrl and HTML should be last
providers = [
    ACM,
    Arxiv,
    CiteSeerX,
    CVF,
    JMLR,
    Nature,
    NBER,
    NeurIPS,
    OpenReview,
    PMLR,
    PubMed,
    SagePub,
    Springer,
    SemanticScholar,
    TandFOnline,
    LocalFile,
    PdfUrl,
    HTML,
]
