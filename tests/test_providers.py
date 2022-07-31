#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "G.J.J. van den Burg"

"""Tests"""

import hashlib
import os
import shutil
import tempfile
import unittest

import pdfplumber

from _constants import TEST_FILE
from pikepdf import Pdf

from paper2remarkable.exceptions import URLResolutionError
from paper2remarkable.providers import ACL
from paper2remarkable.providers import ACM
from paper2remarkable.providers import CVF
from paper2remarkable.providers import ECCC
from paper2remarkable.providers import HTML
from paper2remarkable.providers import IACR
from paper2remarkable.providers import JMLR
from paper2remarkable.providers import NBER
from paper2remarkable.providers import PMLR
from paper2remarkable.providers import Arxiv
from paper2remarkable.providers import CiteSeerX
from paper2remarkable.providers import LocalFile
from paper2remarkable.providers import Nature
from paper2remarkable.providers import NeurIPS
from paper2remarkable.providers import OpenReview
from paper2remarkable.providers import PdfUrl
from paper2remarkable.providers import PubMed
from paper2remarkable.providers import SagePub
from paper2remarkable.providers import ScienceDirect
from paper2remarkable.providers import SemanticScholar
from paper2remarkable.providers import Springer
from paper2remarkable.providers import TandFOnline
from paper2remarkable.utils import download_url

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
        url = "https://dl.acm.org/doi/10.1145/3025453.3026030"
        exp_filename = "Bergstrom-Lehtovirta_Boring_Hornbaek_-_Placing_and_Recalling_Virtual_Items_on_the_Skin_2017.pdf"
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

    def test_acm_3(self):
        prov = ACM(upload=False, verbose=VERBOSE)
        url = "https://dl.acm.org/doi/pdf/10.1145/3442188.3445922"
        exp_filename = "Bender_et_al_-_On_the_Dangers_of_Stochastic_Parrots_Can_Language_Models_Be_Too_Big_2021.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_openreview(self):
        prov = OpenReview(upload=False, verbose=VERBOSE)
        url = "https://openreview.net/forum?id=S1x4ghC9tQ"
        exp_filename = "Gregor_et_al_-_Temporal_Difference_Variational_Auto-Encoder_2019.pdf"
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
        url = "https://link.springer.com/content/pdf/10.1007/11681878_14.pdf"
        exp_filename = "Dwork_et_al_-_Calibrating_Noise_to_Sensitivity_in_Private_Data_Analysis_2006.pdf"
        filename = prov.run(url)
        self.assertEqual(exp_filename, os.path.basename(filename))

    def test_local(self):
        local_filename = "test.pdf"
        with open(local_filename, "w") as fp:
            fp.write(TEST_FILE)
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

    @unittest.skip("T&F Online has been disabled due to CloudFlare blocking")
    def test_tandfonline_1(self):
        prov = TandFOnline(upload=False, verbose=VERBOSE)
        url = "https://www.tandfonline.com/doi/full/10.1080/01621459.2017.1385466"
        exp = "Fearnhead_Rigaill_-_Changepoint_Detection_in_the_Presence_of_Outliers_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    @unittest.skip("T&F Online has been disabled due to CloudFlare blocking")
    def test_tandfonline_2(self):
        prov = TandFOnline(upload=False, verbose=VERBOSE)
        url = "https://www.tandfonline.com/doi/pdf/10.1080/03610918.2017.1408826?needAccess=true"
        exp = "Reschenhofer_-_Heteroscedasticity-Robust_Estimation_of_Autocorrelation_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    @unittest.skip("T&F Online has been disabled due to CloudFlare blocking")
    def test_tandfonline_3(self):
        prov = TandFOnline(upload=False, verbose=VERBOSE)
        url = "https://amstat.tandfonline.com/doi/pdf/10.1080/01621459.2017.1385466?needAccess=true"
        exp = "Fearnhead_Rigaill_-_Changepoint_Detection_in_the_Presence_of_Outliers_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    @unittest.skip("T&F Online has been disabled due to CloudFlare blocking")
    def test_tandfonline_4(self):
        prov = TandFOnline(upload=False, verbose=VERBOSE)
        url = "https://www.tandfonline.com/doi/full/10.1080/0015198X.2019.1675421"
        exp = "Liberman_et_al_-_The_Tax_Benefits_of_Separating_Alpha_From_Beta_2019.pdf"
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

    @unittest.skip("Broken test (other url needed)")
    def test_html_4(self):
        prov = HTML(upload=False, verbose=VERBOSE)
        url = "https://sirupsen.com/2019/"
        filename = prov.run(url)
        # this is a proxy test to check that all images are included
        self.assertEqual(4, len(pdfplumber.open(filename).pages))

    @unittest.skip("Skipping html_5 test")
    def test_html_5(self):
        prov = HTML(upload=False, verbose=VERBOSE)
        url = "https://www.spiegel.de/panorama/london-tausende-rechtsextreme-demonstranten-wollen-statuen-schuetzen-a-2a1ed9b9-708a-40dc-a5ff-f312e97a60ca#"
        filename = prov.run(url)
        # this is a proxy test to check that all images are included
        self.assertEqual(4, len(pdfplumber.open(filename).pages))

    def test_semantic_scholar_1(self):
        prov = SemanticScholar(upload=False, verbose=VERBOSE)
        url = "https://www.semanticscholar.org/paper/Logo-detection-using-weakly-supervised-saliency-map-Kumar-Keserwani/d468069b82fec0c4568478e58826fc372eb24acd"
        with self.assertRaises(URLResolutionError) as cm:
            prov.run(url)
        err = cm.exception
        self.assertEqual(
            err.reason,
            "PDF url on SemanticScholar doesn't point to a pdf file",
        )

    def test_semantic_scholar_2(self):
        prov = SemanticScholar(upload=False, verbose=VERBOSE)
        url = "https://www.semanticscholar.org/paper/Fast-Meta-Learning-for-Adaptive-Hierarchical-Design-Burg-Hero/90759dc4ab0ce8d3564044ef92a91080a4f3e55f"
        exp = "Burg_Hero_-_Fast_Meta-Learning_for_Adaptive_Hierarchical_Classifier_Design_2017.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_semantic_scholar_3(self):
        prov = SemanticScholar(upload=False, verbose=VERBOSE)
        url = "https://www.semanticscholar.org/paper/A-historical-account-of-how-continental-drift-and-Meinhold-%C5%9Eeng%C3%B6r/e7be87319985445e3ef7addf1ebd10899b92441f"
        exp = "Meinhold_Sengor_-_A_Historical_Account_of_How_Continental_Drift_and_Plate_Tectonics_Provided_the_Framework_for_Our_Current_Understanding_of_Palaeogeography_2018.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    @unittest.skip("SagePub has been disabled due to CloudFlare blocking")
    def test_sagepub_1(self):
        prov = SagePub(upload=False, verbose=VERBOSE)
        url = "https://journals.sagepub.com/doi/full/10.1177/0306312714535679"
        exp = "Rekdal_-_Academic_Urban_Legends_2014.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    @unittest.skip("SagePub has been disabled due to CloudFlare blocking")
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

    @unittest.skip(
        "ScienceDirect has been disabled due to CloudFlare blocking"
    )
    def test_sciencedirect_1(self):
        prov = ScienceDirect(upload=False, verbose=VERBOSE)
        url = "https://www.sciencedirect.com/science/article/pii/S0166354220302011"
        exp = "Caly_et_al_-_The_FDA-approved_Drug_Ivermectin_Inhibits_the_Replication_of_SARS-CoV-2_in_Vitro_2020.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    @unittest.skip(
        "ScienceDirect has been disabled due to CloudFlare blocking"
    )
    def test_sciencedirect_2(self):
        prov = ScienceDirect(upload=False, verbose=VERBOSE)
        url = "https://www.sciencedirect.com/science/article/pii/S2352152X2101001X"
        exp = "Mussi_et_al_-_A_Voltage_Dynamic-Based_State_of_Charge_Estimation_Method_for_Batteries_Storage_Systems_2021.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    @unittest.skip(
        "ScienceDirect has been disabled due to CloudFlare blocking"
    )
    def test_sciencedirect_3(self):
        prov = ScienceDirect(upload=False, verbose=VERBOSE)
        url = r"https://pdf.sciencedirectassets.com/272398/1-s2.0-S0022039616X00095/1-s2.0-S0022039616001029/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjELf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCRRFGFc7b02V86pkMeqytyBK%2BR8I%2BfdsIpYbjfXSpIBwIhAORxDxLYdr4EoSyn1P7wlhG%2F1RnX8tIG0IRGOidKKm69KrQDCDAQAxoMMDU5MDAzNTQ2ODY1IgwzsYwSRMjSfdr4cbUqkQOPUxG702LEv3POe5ESC9FBVVHGeUF%2BB46FTtWqkhHgjkRIpuoFiavu1cuBWHQ9FwCZjcocan56LfXiySYBfl259MC8ieSYor9FKZLBaAhDCEblkiTdW2%2Fk4nfogp6fwWVdckC8gGVbu3wQ9Mdh%2FE91ZEix%2FIftmJ6IpAZkm0l0AFFt%2BngI7geWoZDeku5iImEUw6JJPgFz5Yw9cKa%2FuGM3hi29JsuI30qzBqZC9nGRCIx%2FLYeiDfF1v0QjFLmT%2FE5xpaNxMt%2FoWLiazRcconSQCCax6%2Bw9SR4NvWg2illOrLMEPuRYacIFRNhV9zj7Y06Bf%2BfG%2FTQxXdnDLH0VMkUWx%2BgjwRAqSvIb0JRg9q5gErPB1cZLCuCd3ybFSmtj7aQmfl7uhMAjQwnCcN6fhtlVK6Xb3Us7YglDaHekzf8RDv9stbxBWFGMPVmDUXHWOsUo89LY%2F9IbtQTs5Uu3ieMGePUVMY4ox3FPYAb5jWjaOFqs54LqfQ5nqjkLMiAY%2F11zCVyOAoPiDnDs6Wjuj52iszCtuc%2F9BTrqATkmIC%2Bu2w6MEow0zbPVAaqNF%2BjUh8Tv%2BWTInq9G3Q4PXIqL3CNNiISPDvuUggRwWGJDgXtr0C%2B4Gtv1bfs3BGHHgWOD261c6O0LHQuP11BLN8GCr7bFO1hjVAqHhC06vyhGQRmRzN32CPwo8pUM2gWw9xXGUioUiSJ%2FgRpDaszsW4Yr8Wm7L9Q7jAOYxEf7WLxPwAWO69o8JbJoouxwL4qeTEGMJ5IpUk3x3xPQIlawOlqY%2FHi0s4E1DE4ZMjH21hc3PrQ%2FiwI%2BTqY9Rg5sjLCBJ4vRCiqb3dpOWLsR5LFOTySXWoqIdO7b9Q%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20201117T155020Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTY7OS7PK7A%2F20201117%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=03abad117208b684a1a4ca2ffdcbe5b9a40a19e6c841c609e299315a2f2234ce&hash=24f71da9f05f6835c9797841d1462d11eea85c49e9655dde043ed9f748edf17e&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0022039616001029&tid=spdf-6b78a4fa-826e-4267-8ce6-43c814fa51b2&sid=776192553463724f1a4b56613fcf5e514b72gxrqb&type=client"
        exp = "Kristiansen_Wulff_-_Exponential_Estimates_of_Symplectic_Slow_Manifolds_2016.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_acl_1(self):
        prov = ACL(upload=False, verbose=VERBOSE)
        url = "https://www.aclweb.org/anthology/A88-1033/"
        exp = "Newman_-_Combinatorial_Disambiguation_1988.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_acl_2(self):
        prov = ACL(upload=False, verbose=VERBOSE)
        url = "https://www.aclweb.org/anthology/2020.acl-main.79.pdf"
        exp = "Zhong_et_al_-_Interpreting_Twitter_User_Geolocation_2020.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_acl_3(self):
        prov = ACL(upload=False, verbose=VERBOSE)
        url = "https://www.aclweb.org/anthology/2020.sigmorphon-1.29v2.pdf"
        exp = (
            "Burness_McMullin_-_Multi-Tiered_Strictly_Local_Functions_2020.pdf"
        )
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_local_file_copy_toc(self):
        """Make sure the table of content is kept after processing."""
        local_filename = "test.pdf"
        download_url("https://arxiv.org/pdf/1711.03512.pdf", local_filename)
        prov = LocalFile(upload=False, verbose=VERBOSE)
        filename = prov.run(local_filename)
        with Pdf.open(filename) as pdf:
            with pdf.open_outline() as outline:
                assert len(outline.root) > 0

    def test_arxiv_copy_toc(self):
        """Make sure the table of content is kept after processing when using the arXiv provider."""
        prov = Arxiv(upload=False, verbose=VERBOSE)
        filename = prov.run("https://arxiv.org/abs/1711.03512")
        with Pdf.open(filename) as pdf:
            with pdf.open_outline() as outline:
                assert len(outline.root) > 0

    def test_eccc_1(self):
        prov = ECCC(upload=False, verbose=VERBOSE)
        url = "https://eccc.weizmann.ac.il/report/2021/063/"
        exp = "Chou_et_al_-_Approximability_of_All_Finite_CSPs_in_the_Dynamic_Streaming_Setting_2021.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_eccc_2(self):
        prov = ECCC(upload=False, verbose=VERBOSE)
        url = "https://eccc.weizmann.ac.il/report/2007/003/"
        exp = "Cai_Lu_-_Bases_Collapse_in_Holographic_Algorithms_2007.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_eccc_3(self):
        prov = ECCC(upload=False, verbose=VERBOSE)
        url = "https://eccc.weizmann.ac.il/report/1998/052/download"
        exp = (
            "Hemkemeier_Vallentin_-_On_the_Decomposition_of_Lattices_1998.pdf"
        )
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_iacr_1(self):
        prov = IACR(upload=False, verbose=VERBOSE)
        url = "https://eprint.iacr.org/2021/490"
        exp = "Liu_Wang_Zheng_-_Optimizing_Bootstrapping_and_Evaluating_Large_FHE_Gates_in_the_LWE-based_GSW-FHE_2021.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_iacr_2(self):
        prov = IACR(upload=False, verbose=VERBOSE)
        url = "https://eprint.iacr.org/2007/474.pdf"
        exp = "Cochran_-_Notes_on_the_Wang_Et_Al._2_63_SHA-1_Differential_Path_2007.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))

    def test_iacr_3(self):
        prov = IACR(upload=False, verbose=VERBOSE)
        url = "http://eprint.iacr.org/1996/008"
        exp = "Naor_Wool_-_Access_Control_and_Signatures_via_Quorum_Secret_Sharing_1996.pdf"
        filename = prov.run(url)
        self.assertEqual(exp, os.path.basename(filename))


if __name__ == "__main__":
    unittest.main()
