"""
Basic unit test suite.
"""
import logging
from unittest import skipUnless

from . import shared

from doekbase.data_api.sequence.assembly import AssemblyAPI
from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI

_log = logging.getLogger(__name__)

def setup():
    shared.setup()

def teardown():
    pass

@skipUnless(shared.can_connect(), 'Cannot connect to workspace')
def test_assembly_api():
    """Testing Assembly API"""
    _log.info("{} with {}".format("test_assembly_api", shared.genome + "_assembly"))
    ci_assembly_api = AssemblyAPI(services=shared.services,
                                  token=shared.token,
                                  ref=shared.genome + "_assembly")
    subset_contigs = ci_assembly_api.get_contigs(["kb|g.3157.c.0"])
    _log.debug("Got contigs: {}".format(subset_contigs))
    assert len(subset_contigs) == 1

@skipUnless(shared.can_connect(), 'Cannot connect to workspace')
def test_genome_annotation_api():
    """Testing Genome Annotation API"""
    _log.info("{} with {}".format("test_genome_annotation_api", shared.genome))
    ci_genome_annotation_api = GenomeAnnotationAPI(services=shared.services,
                                                   token=shared.token,
                                                   ref=shared.genome)
    subset_features = ci_genome_annotation_api.get_features(["kb|g.3157.peg.0"])
    _log.debug("Got features: {}".format(subset_features))
    assert len(subset_features) == 1

@skipUnless(shared.can_connect(), 'Cannot connect to workspace')
def test_taxon_api():
    """Testing Taxon API"""
    _log.info("{} with {}".format("test_taxon_api", shared.genome))
    ci_taxon_api = GenomeAnnotationAPI(services=shared.services,
                                       token=shared.token,
                                       ref=shared.genome).get_taxon()
    scientific_name = ci_taxon_api.get_scientific_name()
    _log.debug("Got scientific_name: {}".format(scientific_name))
    assert len(scientific_name) > 0