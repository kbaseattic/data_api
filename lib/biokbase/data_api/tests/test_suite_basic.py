"""
Basic unit test suite.
"""
# Stdlib
import logging
from unittest import skipUnless
# Local
from . import shared
from biokbase.data_api.sequence.assembly import AssemblyAPI
from biokbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI

_log = logging.getLogger(__name__)

services = {}

workspaces = {
    '3157': {
        'gene': 'PrototypeReferenceGenomes/kb|g.3157',
        'features': 'PrototypeReferenceGenomes/kb|g.3157.peg.0',
        'contigs': 'PrototypeReferenceGenomes/kb|g.3157.c.0'
    }
}

def setup():
    shared.setup()
    services.update(shared.get_services())
    shared.determine_can_connect(workspaces)

def teardown():
    shared.teardown()

_ws = workspaces['3157']

@skipUnless(_ws['gene'] and _ws['contigs'], shared.connect_fail)
def test_assembly_api():
    _log.debug("Fetching kb|g.3157.c.0")
    ci_assembly_api = AssemblyAPI(services=services,
                                  ref=shared.genome + "_assembly")
    subset_contigs = ci_assembly_api.get_contigs(["kb|g.3157.c.0"])
    _log.debug("Got contigs: {}".format(subset_contigs))
    assert len(subset_contigs) == 1

@skipUnless(_ws['gene'] and _ws['features'], shared.connect_fail)
def test_genome_annotation_api():
    _log.debug("Fetching kb|g.3157.peg.0")
    ci_genome_annotation_api = GenomeAnnotationAPI(services=services,
                                                   ref=shared.genome)
    subset_features = ci_genome_annotation_api.get_features(["kb|g.3157.peg.0"])
    print subset_features
    assert len(subset_features) == 1

@skipUnless(_ws['gene'], shared.connect_fail)
def test_taxon_api():
    _log.debug("Fetching taxon for kb|g.3157")
    ci_taxon_api = GenomeAnnotationAPI(services=services,
                                       ref=shared.genome).get_taxon()
    scientific_name = ci_taxon_api.get_scientific_name()
    print scientific_name
    assert len(scientific_name) > 0
    