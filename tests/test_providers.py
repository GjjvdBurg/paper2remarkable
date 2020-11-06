#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "G.J.J. van den Burg"

"""Tests"""

import hashlib
import os
import pdfplumber
import shutil
import tempfile
import unittest

from paper2remarkable.providers import (
    ACM,
    Arxiv,
    CVF,
    CiteSeerX,
    HTML,
    JMLR,
    LocalFile,
    Nature,
    NBER,
    NeurIPS,
    OpenReview,
    PMLR,
    PdfUrl,
    PubMed,
    SagePub,
    SemanticScholar,
    Springer,
    TandFOnline,
)

VERBOSE = False


def md5sum(filename):
    blocksize = 65536
    hasher = hashlib.md5()
    with open(filename, "rb") as fid:
        buf = fid.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fid.read(blocksize)
    return hasher.hexdigest()


class TestProviders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_dir = os.getcwd()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_arxiv_1(self):
        # check with qpdf
        prov = Arxiv(upload=False, verbose=VERBOSE, pdftk_path=None)
        url = "https://arxiv.org/abs/1811.11242v1"
        exp_filename = "Burg_Nazabal_Sutton_-_Wrangling_Messy_CSV_Files_by_Detecting_Row_and_Type_Patterns_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_arxiv_2(self):
        prov = Arxiv(upload=False, verbose=VERBOSE)
        url = "http://arxiv.org/abs/arXiv:1908.03213"
        exp_filename = "Ecker_et_al_-_Gravitational_Waves_From_Holographic_Neutron_Star_Mergers_2019.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_arxiv_3(self):
        prov = Arxiv(upload=False, verbose=VERBOSE)
        url = "https://arxiv.org/abs/math/0309285"
        exp_filename = "Jackson_et_al_-_An_Algorithm_for_Optimal_Partitioning_of_Data_on_an_Interval_2003.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_arxiv_4(self):
        prov = Arxiv(upload=False, verbose=VERBOSE)
        url = "https://arxiv.org/pdf/physics/0605197v1.pdf"
        exp_filename = (
            "Knuth_-_Optimal_Data-Based_Binning_for_Histograms_2006.pdf"
        )
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_arxiv_5(self):
        prov = Arxiv(upload=False, verbose=VERBOSE, qpdf_path=None)
        url = "https://arxiv.org/abs/2002.11523"
        exp_filename = "Ponomarev_Oseledets_Cichocki_-_Using_Reinforcement_Learning_in_the_Algorithmic_Trading_Problem_2020.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_arxiv_6(self):
        prov = Arxiv(upload=False, verbose=VERBOSE)
        url = "https://arxiv.org/pdf/1701.05517.pdf?source=post_page---------------------------"
        exp_filename = "Salimans_et_al_-_PixelCNN_Improving_the_PixelCNN_With_Discretized_Logistic_Mixture_Likelihood_and_Other_Modifications_2017.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_pmc(self):
        prov = PubMed(upload=False, verbose=VERBOSE)
        url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3474301/"
        exp_filename = (
            "Hoogenboom_Manske_-_How_to_Write_a_Scientific_Article_2012.pdf"
        )
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_acm_1(self):
        prov = ACM(upload=False, verbose=VERBOSE)
        url = "https://dl.acm.org/citation.cfm?id=3025626"
        exp_filename = "Kery_Horvath_Myers_-_Variolite_Supporting_Exploratory_Programming_by_Data_Scientists_2017.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_acm_2(self):
        prov = ACM(upload=False, verbose=VERBOSE)
        url = (
            "https://dl.acm.org/doi/pdf/10.1145/3219819.3220081?download=true"
        )
        exp_filename = "Bateni_Esfandiari_Mirrokni_-_Optimal_Distributed_Submodular_Optimization_via_Sketching_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_openreview(self):
        prov = OpenReview(upload=False, verbose=VERBOSE)
        url = "https://openreview.net/forum?id=S1x4ghC9tQ"
        exp_filename = "Gregor_et_al_-_Temporal_Difference_Variational_Auto-Encoder_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_springer_1(self):
        prov = Springer(upload=False, verbose=VERBOSE)
        url = "https://link.springer.com/article/10.1007/s10618-019-00631-5"
        exp_filename = "Mauw_Ramirez-Cruz_Trujillo-Rasua_-_Robust_Active_Attacks_on_Social_Graphs_2019.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_springer_2(self):
        prov = Springer(upload=False, verbose=VERBOSE)
        url = "https://link.springer.com/content/pdf/10.1007%2F11681878_14.pdf"
        exp_filename = "Dwork_et_al_-_Calibrating_Noise_to_Sensitivity_in_Private_Data_Analysis_2006.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_local(self):
        local_filename = "test.pdf"
        with open(local_filename, "w") as fp:
            fp.write(
                "%PDF-1.1\n%¥±ë\n\n1 0 obj\n  << /Type /Catalog\n     /Pages 2 0 R\n  >>\nendobj\n\n2 0 obj\n  << /Type /Pages\n     /Kids [3 0 R]\n     /Count 1\n     /MediaBox [0 0 300 144]\n  >>\nendobj\n\n3 0 obj\n  <<  /Type /Page\n      /Parent 2 0 R\n      /Resources\n       << /Font\n           << /F1\n               << /Type /Font\n                  /Subtype /Type1\n                  /BaseFont /Times-Roman\n               >>\n           >>\n       >>\n      /Contents 4 0 R\n  >>\nendobj\n\n4 0 obj\n  << /Length 55 >>\nstream\n  BT\n    /F1 18 Tf\n    0 0 Td\n    (Hello World) Tj\n  ET\nendstream\nendobj\n\nxref\n0 5\n0000000000 65535 f \n0000000018 00000 n \n0000000077 00000 n \n0000000178 00000 n \n0000000457 00000 n \ntrailer\n  <<  /Root 1 0 R\n      /Size 5\n  >>\nstartxref\n565\n%%EOF"
            )
        prov = LocalFile(upload=False, verbose=VERBOSE)
        filename = prov.run(local_filename)
        self.assertEqual("test_.pdf", os.path.basename(filename))

    def test_pdfurl_1(self):
        prov = PdfUrl(upload=False, verbose=VERBOSE)
        url = "http://www.jmlr.org/papers/volume17/14-526/14-526.pdf"
        filename = prov.run(url)
        self.assertEqual("14-526.pdf", os.path.basename(filename))

    def test_pdfurl_2(self):
        prov = PdfUrl(upload=False, verbose=VERBOSE)
        url = "https://www.manuelrigger.at/preprints/NoREC.pdf"
        filename = prov.run(url)
        self.assertEqual("NoREC.pdf", os.path.basename(filename))

    def test_jmlr_1(self):
        prov = JMLR(upload=False, verbose=VERBOSE)
        url = "http://www.jmlr.org/papers/volume17/14-526/14-526.pdf"
        exp = "Burg_Groenen_-_GenSVM_a_Generalized_Multiclass_Support_Vector_Machine_2016.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_jmlr_2(self):
        prov = JMLR(upload=False, verbose=VERBOSE)
        url = "http://www.jmlr.org/papers/v10/xu09a.html"
        exp = "Xu_Zhang_-_Refinement_of_Reproducing_Kernels_2009.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_pmlr_1(self):
        prov = PMLR(upload=False, verbose=VERBOSE)
        url = "http://proceedings.mlr.press/v97/behrmann19a.html"
        exp = "Behrmann_et_al_-_Invertible_Residual_Networks_2019.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_pmlr_2(self):
        prov = PMLR(upload=False, verbose=VERBOSE)
        url = "http://proceedings.mlr.press/v15/maaten11b/maaten11b.pdf"
        exp = "Maaten_Welling_Saul_-_Hidden-Unit_Conditional_Random_Fields_2011.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_pmlr_3(self):
        prov = PMLR(upload=False, verbose=VERBOSE)
        url = "http://proceedings.mlr.press/v48/melnyk16.pdf"
        exp = "Melnyk_Banerjee_-_Estimating_Structured_Vector_Autoregressive_Models_2016.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_pmlr_4(self):
        prov = PMLR(upload=False, verbose=VERBOSE)
        url = "http://proceedings.mlr.press/v48/zhangf16.html"
        exp = "Zhang_Paisley_-_Markov_Latent_Feature_Models_2016.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_nber_1(self):
        prov = NBER(upload=False, verbose=VERBOSE)
        url = "https://www.nber.org/papers/w26752"
        exp = "Bhattacharya_Packalen_-_Stagnation_and_Scientific_Incentives_2020.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_nber_2(self):
        prov = NBER(upload=False, verbose=VERBOSE)
        url = "https://www.nber.org/papers/w19152.pdf"
        exp = "Herbst_Schorfheide_-_Sequential_Monte_Carlo_Sampling_for_DSGE_Models_2013.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_neurips_1(self):
        prov = NeurIPS(upload=False, verbose=VERBOSE)
        url = "https://papers.nips.cc/paper/325-leaning-by-combining-memorization-and-gradient-descent.pdf"
        exp = "Platt_-_Leaning_by_Combining_Memorization_and_Gradient_Descent_1990.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_neurips_2(self):
        prov = NeurIPS(upload=False, verbose=VERBOSE)
        url = "https://papers.nips.cc/paper/7796-middle-out-decoding"
        exp = "Mehri_Sigal_-_Middle-Out_Decoding_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_neurips_3(self):
        prov = NeurIPS(upload=False, verbose=VERBOSE)
        url = "http://papers.neurips.cc/paper/5433-combinatorial-pure-exploration-of-multi-armed-bandits"
        exp = "Chen_et_al_-_Combinatorial_Pure_Exploration_of_Multi-Armed_Bandits_2014.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_neurips_4(self):
        prov = NeurIPS(upload=False, verbose=VERBOSE)
        url = "http://papers.neurips.cc/paper/7368-on-the-dimensionality-of-word-embedding.pdf"
        exp = "Yin_Shen_-_On_the_Dimensionality_of_Word_Embedding_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_citeseerx_1(self):
        prov = CiteSeerX(upload=False, verbose=VERBOSE)
        url = "http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.89.6548"
        exp = "Aaronson_-_Is_P_Versus_NP_Formally_Independent_2003.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_citeseerx_2(self):
        prov = CiteSeerX(upload=False, verbose=VERBOSE)
        url = "http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.123.7607&rep=rep1&type=pdf"
        exp = "Kirkpatrick_Gelatt_Vecchi_-_Optimization_by_Simulated_Annealing_1983.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_tandfonline_1(self):
        prov = TandFOnline(upload=False, verbose=VERBOSE)
        url = "https://www.tandfonline.com/doi/full/10.1080/01621459.2017.1385466"
        exp = "Fearnhead_Rigaill_-_Changepoint_Detection_in_the_Presence_of_Outliers_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_tandfonline_2(self):
        prov = TandFOnline(upload=False, verbose=VERBOSE)
        url = "https://www.tandfonline.com/doi/pdf/10.1080/03610918.2017.1408826?needAccess=true"
        exp = "Reschenhofer_-_Heteroscedasticity-Robust_Estimation_of_Autocorrelation_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_tandfonline_3(self):
        prov = TandFOnline(upload=False, verbose=VERBOSE)
        url = "https://amstat.tandfonline.com/doi/pdf/10.1080/01621459.2017.1385466?needAccess=true"
        exp = "Fearnhead_Rigaill_-_Changepoint_Detection_in_the_Presence_of_Outliers_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_html_1(self):
        prov = HTML(upload=False, verbose=VERBOSE)
        url = "https://hbr.org/2019/11/getting-your-team-to-do-more-than-meet-deadlines"
        exp = "Getting_Your_Team_to_Do_More_Than_Meet_Deadlines.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_html_2(self):
        prov = HTML(upload=False, verbose=VERBOSE)
        url = "https://www.nature.com/articles/d41586-020-00176-4"
        exp = "Isaac_Asimov_Centenary_of_the_Great_Explainer.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_html_3(self):
        prov = HTML(upload=False, verbose=VERBOSE)
        url = "https://conclave-team.github.io/conclave-site/"
        # exp = "Conclave_Case_Study_-_A_Private_and_Secure_Real-Time_Collaborative_Text_Editor.pdf"
        # NOTE: Title differs between Readability.JS and readability-lxml, we
        # assume that testing is done with Readability.JS
        exp = "Conclave.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))
        # this is a proxy test to check that all images are included
        self.assertEqual(32, len(pdfplumber.open(filename).pages))

    def test_html_4(self):
        prov = HTML(upload=False, verbose=VERBOSE)
        url = "https://sirupsen.com/2019/"
        filename = prov.run(url)
        # this is a proxy test to check that all images are included
        self.assertEqual(4, len(pdfplumber.open(filename).pages))

    def test_html_5(self):
        prov = HTML(upload=False, verbose=VERBOSE)
        url = "https://www.spiegel.de/panorama/london-tausende-rechtsextreme-demonstranten-wollen-statuen-schuetzen-a-2a1ed9b9-708a-40dc-a5ff-f312e97a60ca#"
        filename = prov.run(url)
        # this is a proxy test to check that all images are included
        self.assertEqual(4, len(pdfplumber.open(filename).pages))

    def test_semantic_scholar_1(self):
        prov = SemanticScholar(upload=False, verbose=VERBOSE)
        url = "https://pdfs.semanticscholar.org/1b01/dea77e9cbf049b4ee8b68dc4d43529d06299.pdf"
        exp = "Dong_et_al_-_TableSense_Spreadsheet_Table_Detection_With_Convolutional_Neural_Networks_2019.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_semantic_scholar_2(self):
        prov = SemanticScholar(upload=False, verbose=VERBOSE)
        url = "https://www.semanticscholar.org/paper/Fast-Meta-Learning-for-Adaptive-Hierarchical-Design-Burg-Hero/90759dc4ab0ce8d3564044ef92a91080a4f3e55f"
        exp = "Burg_Hero_-_Fast_Meta-Learning_for_Adaptive_Hierarchical_Classifier_Design_2017.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_sagepub_1(self):
        prov = SagePub(upload=False, verbose=VERBOSE)
        url = "https://journals.sagepub.com/doi/full/10.1177/0306312714535679"
        exp = "Rekdal_-_Academic_Urban_Legends_2014.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_sagepub_2(self):
        prov = SagePub(upload=False, verbose=VERBOSE)
        url = "https://journals.sagepub.com/doi/pdf/10.1177/1352458517694432"
        exp = "Kobelt_et_al_-_New_Insights_Into_the_Burden_and_Costs_of_Multiple_Sclerosis_in_Europe_2017.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_cvf_1(self):
        prov = CVF(upload=False, verbose=VERBOSE)
        url = "https://openaccess.thecvf.com/content_ICCV_2019/html/Muhammad_Goal-Driven_Sequential_Data_Abstraction_ICCV_2019_paper.html"
        exp = (
            "Muhammad_et_al_-_Goal-Driven_Sequential_Data_Abstraction_2019.pdf"
        )
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_cvf_2(self):
        prov = CVF(upload=False, verbose=VERBOSE)
        url = "https://openaccess.thecvf.com/content_CVPR_2020/papers/Park_Seeing_the_World_in_a_Bag_of_Chips_CVPR_2020_paper.pdf"
        exp = (
            "Park_Holynski_Seitz_-_Seeing_the_World_in_a_Bag_of_Chips_2020.pdf"
        )
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_nature_1(self):
        prov = Nature(upload=False, verbose=VERBOSE)
        url = "https://www.nature.com/articles/s41598-020-75456-0"
        exp = "Golozar_et_al_-_Direct_Observation_of_Lithium_Metal_Dendrites_With_Ceramic_Solid_Electrolyte_2020.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_nature_2(self):
        prov = Nature(upload=False, verbose=VERBOSE)
        url = "https://www.nature.com/articles/s41599-019-0371-1.pdf"
        exp = "Leroi_et_al_-_On_Revolutions_2020.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))


if __name__ == "__main__":
    unittest.main()
