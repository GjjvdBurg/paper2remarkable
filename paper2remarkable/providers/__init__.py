# -*- coding: utf-8 -*-

from .acl import ACL
from .acm import ACM
from .arxiv import Arxiv
from .cvf import CVF
from .diva import DiVA
from .eccc import ECCC
from .html import HTML
from .iacr import IACR
from .jmlr import JMLR
from .local import LocalFile
from .nature import Nature
from .nber import NBER
from .neurips import NeurIPS
from .openreview import OpenReview
from .pdf_url import PdfUrl
from .pmlr import PMLR
from .pubmed import PubMed
from .semantic_scholar import SemanticScholar
from .springer import Springer

# # The following providers are no longer functional due to Cloudflare blocking
# # automated access, and have therefore been removed from the list of providers
# # below.
# from .citeseerx import CiteSeerX  # disabled, incomplete html doc received
# from .sagepub import SagePub
# from .science_direct import ScienceDirect
# from .tandfonline import TandFOnline

# NOTE: Order matters here, PdfUrl and HTML should be last
providers = [
    ACL,
    ACM,
    Arxiv,
    CVF,
    DiVA,
    ECCC,
    IACR,
    JMLR,
    Nature,
    NBER,
    NeurIPS,
    OpenReview,
    PMLR,
    PubMed,
    Springer,
    SemanticScholar,
    LocalFile,
    PdfUrl,
    HTML,
]
