"""
Unit tests for genome_annotation
"""
import logging
from unittest import skipUnless

from . import shared

from doekbase.data_api.taxonomy.taxon.api import TaxonAPI

_log = logging.getLogger(__name__)

taxon_new = "ReferenceTaxons/242159_taxon"
taxon_old = "OriginalReferenceGenomes/kb|g.166819"
t_new = None
t_old = None

def setup():
    shared.setup()
    global t_new, t_old
    t_new = TaxonAPI(shared.services, shared.token, taxon_new)
    t_old = TaxonAPI(shared.services, shared.token, taxon_old)

####### New Taxon Type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_parent_new():
    _log.info("Input {}".format(taxon_new))
    parent = t_new.get_parent()
    _log.info("Output {}".format(parent))
    assert isinstance(parent, TaxonAPI)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_children_new():
    _log.info("Input {}".format(taxon_new))
    children = t_new.get_children()
    _log.info("Output {}".format(children))
    assert isinstance(children, list)
    #and len(children) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genome_annotations_new():
    _log.info("Input {}".format(taxon_new))
    annotations = t_new.get_genome_annotations()
    _log.info("Output {}".format(annotations))
    assert isinstance(annotations, list)
    #and len(annotations) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_scientific_lineage_new():
    _log.info("Input {}".format(taxon_new))
    scientific_lineage = t_new.get_scientific_lineage()
    _log.info("Output {}".format(scientific_lineage))
    assert isinstance(scientific_lineage, basestring) and len(scientific_lineage) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_scientific_name_new():
    _log.info("Input {}".format(taxon_new))
    scientific_name = t_new.get_scientific_name()
    _log.info("Output {}".format(scientific_name))
    assert isinstance(scientific_name, basestring) and len(scientific_name) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_taxonomic_id_new():
    _log.info("Input {}".format(taxon_new))
    taxonomic_id = t_new.get_taxonomic_id()
    _log.info("Output {}".format(taxonomic_id))
    assert isinstance(taxonomic_id, int) and taxonomic_id != -1


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_kingdom_new():
    _log.info("Input {}".format(taxon_new))
    kingdom = t_new.get_kingdom()
    _log.info("Output {}".format(kingdom))
    assert kingdom == "Viridiplantae"


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_domain_new():
    _log.info("Input {}".format(taxon_new))
    domain = t_new.get_domain()
    _log.info("Output {}".format(domain))
    assert isinstance(domain, basestring) and len(domain) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_aliases_new():
    _log.info("Input {}".format(taxon_new))
    aliases = t_new.get_aliases()
    _log.info("Output {}".format(aliases))
    assert isinstance(aliases, list) and len(aliases) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genetic_code_new():
    _log.info("Input {}".format(taxon_new))
    genetic_code = t_new.get_genetic_code()
    _log.info("Output {}".format(genetic_code))
    assert isinstance(genetic_code, int) and genetic_code != -1


####### Old Taxon Type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_parent_old():
    _log.info("Input {}".format(taxon_old))
    parent = t_old.get_parent()
    _log.info("Output {}".format(parent))
    assert parent is None


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_children_old():
    _log.info("Input {}".format(taxon_old))
    children = t_old.get_children()
    _log.info("Output {}".format(children))
    assert isinstance(children, list) and len(children) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genome_annotations_old():
    _log.info("Input {}".format(taxon_old))
    annotations = t_old.get_genome_annotations()
    _log.info("Output {}".format(annotations))
    assert isinstance(annotations, list) and len(annotations) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_scientific_lineage_old():
    _log.info("Input {}".format(taxon_old))
    scientific_lineage = t_old.get_scientific_lineage()
    _log.info("Output {}".format(scientific_lineage))
    assert isinstance(scientific_lineage, basestring) and len(scientific_lineage) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_scientific_name_old():
    _log.info("Input {}".format(taxon_old))
    scientific_name = t_old.get_scientific_name()
    _log.info("Output {}".format(scientific_name))
    assert isinstance(scientific_name, basestring) and len(scientific_name) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_taxonomic_id_old():
    _log.info("Input {}".format(taxon_old))
    taxonomic_id = t_old.get_taxonomic_id()
    _log.info("Output {}".format(taxonomic_id))
    assert isinstance(taxonomic_id, int) and taxonomic_id == -1


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_kingdom_old():
    _log.info("Input {}".format(taxon_old))
    kingdom = t_old.get_kingdom()
    print kingdom
    _log.info("Output {}".format(kingdom))
    assert kingdom is None


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_domain_old():
    _log.info("Input {}".format(taxon_old))
    domain = t_old.get_domain()
    _log.info("Output {}".format(domain))
    assert isinstance(domain, basestring) and len(domain) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_aliases_old():
    _log.info("Input {}".format(taxon_old))
    aliases = t_old.get_aliases()
    _log.info("Output {}".format(aliases))
    assert isinstance(aliases, list) and len(aliases) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genetic_code_old():
    _log.info("Input {}".format(taxon_old))
    genetic_code = t_old.get_genetic_code()
    _log.info("Output {}".format(genetic_code))
    assert isinstance(genetic_code, int) and genetic_code != -1
