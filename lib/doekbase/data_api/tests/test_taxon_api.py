"""
Unit tests for genome_annotation
"""
import logging
from unittest import skipUnless

from . import shared

from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.taxonomy.taxon.api import _Taxon
from doekbase.data_api.taxonomy.taxon.api import _KBaseGenomes_Genome
from doekbase.data_api.taxonomy.taxon.api import TaxonClientAPI

_log = logging.getLogger(__name__)

taxon_new = "ReferenceTaxons/242159_taxon"
taxon_old = "OriginalReferenceGenomes/kb|g.166819"
t_new = None
t_new_e = None
t_old = None
t_old_e = None
t_client_new = None
t_client_old = None

def setup():
    shared.setup()
    global t_new, t_new_e, t_old, t_old_e, t_client_new, t_client_old
    t_new = TaxonAPI(shared.services, shared.token, taxon_new)
    t_new_e = _Taxon(shared.services, shared.token, taxon_new)
    t_old = TaxonAPI(shared.services, shared.token, taxon_old)
    t_old_e = _KBaseGenomes_Genome(shared.services, shared.token, taxon_old)
    _log.info("Connecting to Taxon Thrift Service at {}".format(shared.services["taxon_service_url"]))
    t_client_new = TaxonClientAPI(shared.services["taxon_service_url"], shared.token, taxon_new)
    t_client_old = TaxonClientAPI(shared.services["taxon_service_url"], shared.token, taxon_old)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_bogus_type():
    inputs = ["Bogus",
              "ReferenceGenomeAnnotations/kb|g.166819",
              "ReferenceGenomeAnnotations/kb|g.166819_assembly",
              "OriginalReferenceGenomes/kb|g.166819.contigset"]
    _log.info("Input {}".format(inputs))
    for x in inputs:
        try:
            t = TaxonAPI(shared.services, shared.token, x)
        except Exception, e:
            assert isinstance(e, TypeError)


####### New Taxon Type tests, library


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_parent_new():
    _log.info("Input {}".format(taxon_new))
    parent = t_new.get_parent()
    _log.info("Output {}".format(parent))
    assert isinstance(parent, TaxonAPI)
    parent_e = t_new_e.get_parent()
    assert isinstance(parent_e, TaxonAPI)
    assert parent.get_taxonomic_id() == parent_e.get_taxonomic_id()
    parent_c = t_client_new.get_parent()
    assert isinstance(parent_c, TaxonClientAPI)
    assert parent.get_taxonomic_id() == parent_c.get_taxonomic_id()


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_children_new():
    _log.info("Input {}".format(taxon_new))
    children = t_new.get_children()
    _log.info("Output {}".format(children))
    assert isinstance(children, list)
    #and len(children) > 0
    children_e = t_new_e.get_children()
    assert isinstance(children_e, list)
    assert children == children_e, \
        "Children mismatch {} != {}".format(
            ','.join([str(x) for x in children]),
            ','.join([str(x) for x in children_e]))
    children_c = t_client_new.get_children()
    assert isinstance(children_c, list)
    assert children == children_c, \
        "Children mismatch {} != {}".format(
            ','.join([str(x) for x in children]),
            ','.join([str(x) for x in children_c]))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genome_annotations_new():
    _log.info("Input {}".format(taxon_new))
    annotations = t_new.get_genome_annotations()
    _log.info("Output {}".format(annotations))
    assert isinstance(annotations, list)
    #and len(annotations) > 0
    annotations_e = t_new_e.get_genome_annotations()
    assert isinstance(annotations_e, list)
    assert annotations == annotations_e, \
        "Annotation mismatch {} != {}".format(
            ','.join(map(str, annotations)),
            ','.join(map(str, annotations_e)))
    annotations_c = t_client_new.get_genome_annotations()
    assert isinstance(annotations_c, list)
    assert annotations == annotations_c, \
        "Annotation mismatch {} != {}".format(
            ','.join(map(str, annotations)),
            ','.join(map(str, annotations_c)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_scientific_lineage_new():
    _log.info("Input {}".format(taxon_new))
    scientific_lineage = t_new.get_scientific_lineage()
    _log.info("Output {}".format(scientific_lineage))
    assert isinstance(scientific_lineage, list) and len(scientific_lineage) > 0
    scientific_lineage_e = t_new_e.get_scientific_lineage()
    assert isinstance(scientific_lineage_e, list) and len(scientific_lineage_e) > 0
    assert scientific_lineage == scientific_lineage_e
    scientific_lineage_c = t_client_new.get_scientific_lineage()
    assert isinstance(scientific_lineage_c, list) and len(scientific_lineage_c) > 0
    assert scientific_lineage == scientific_lineage_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_scientific_name_new():
    _log.info("Input {}".format(taxon_new))
    scientific_name = t_new.get_scientific_name()
    _log.info("Output {}".format(scientific_name))
    assert isinstance(scientific_name, basestring) and len(scientific_name) > 0
    scientific_name_e = t_new_e.get_scientific_name()
    assert isinstance(scientific_name_e, basestring) and len(scientific_name_e) > 0
    assert scientific_name == scientific_name_e
    scientific_name_c = t_client_new.get_scientific_name()
    assert isinstance(scientific_name_c, basestring) and len(scientific_name_c) > 0
    assert scientific_name == scientific_name_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_taxonomic_id_new():
    _log.info("Input {}".format(taxon_new))
    taxonomic_id = t_new.get_taxonomic_id()
    _log.info("Output {}".format(taxonomic_id))
    assert isinstance(taxonomic_id, int) and taxonomic_id != -1
    taxonomic_id_e = t_new_e.get_taxonomic_id()
    assert isinstance(taxonomic_id_e, int) and taxonomic_id_e != -1
    assert taxonomic_id == taxonomic_id_e
    taxonomic_id_c = t_client_new.get_taxonomic_id()
    assert isinstance(taxonomic_id_c, int) and taxonomic_id_c != -1
    assert taxonomic_id == taxonomic_id_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_kingdom_new():
    _log.info("Input {}".format(taxon_new))
    kingdom = t_new.get_kingdom()
    _log.info("Output {}".format(kingdom))
    assert kingdom == "Viridiplantae"
    kingdom_e = t_new_e.get_kingdom()
    assert kingdom_e == "Viridiplantae"
    kingdom_c = t_client_new.get_kingdom()
    assert kingdom_c == "Viridiplantae"


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_domain_new():
    _log.info("Input {}".format(taxon_new))
    domain = t_new.get_domain()
    _log.info("Output {}".format(domain))
    assert isinstance(domain, basestring) and len(domain) > 0
    domain_e = t_new_e.get_domain()
    assert isinstance(domain_e, basestring) and len(domain_e) > 0
    assert domain == domain_e
    domain_c = t_client_new.get_domain()
    assert isinstance(domain_c, basestring) and len(domain_c) > 0
    assert domain == domain_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_aliases_new():
    _log.info("Input {}".format(taxon_new))
    aliases = t_new.get_aliases()
    _log.info("Output {}".format(aliases))
    assert isinstance(aliases, list) and len(aliases) > 0
    aliases_e = t_new_e.get_aliases()
    assert isinstance(aliases_e, list) and len(aliases_e) > 0
    assert aliases == aliases_e
    aliases_c = t_client_new.get_aliases()
    assert isinstance(aliases_c, list) and len(aliases_c) > 0
    assert aliases == aliases_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genetic_code_new():
    _log.info("Input {}".format(taxon_new))
    genetic_code = t_new.get_genetic_code()
    _log.info("Output {}".format(genetic_code))
    assert isinstance(genetic_code, int) and genetic_code != -1
    genetic_code_e = t_new_e.get_genetic_code()
    assert isinstance(genetic_code_e, int) and genetic_code_e != -1
    assert genetic_code == genetic_code_e
    genetic_code_c = t_client_new.get_genetic_code()
    assert isinstance(genetic_code_c, int) and genetic_code_c != -1
    assert genetic_code == genetic_code_c


####### Old Taxon Type tests, library


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_parent_old():
    _log.info("Input {}".format(taxon_old))
    try:
        parent = t_old.get_parent()
        _log.info("Output {}".format(parent))
    except AttributeError:
        assert True
    else:
        assert False

    try:
        parent_e = t_old_e.get_parent()
    except AttributeError:
        assert True
    else:
        assert False

    try:
        parent_c = t_client_old.get_parent()
    except AttributeError:
        assert True
    else:
        assert False


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_children_old():
    _log.info("Input {}".format(taxon_old))
    children = t_old.get_children()
    _log.info("Output {}".format(children))
    assert isinstance(children, list) and len(children) == 0
    children_e = t_old_e.get_children()
    assert isinstance(children_e, list) and len(children_e) == 0
    assert children == children_e
    children_c = t_client_old.get_children()
    assert isinstance(children_c, list) and len(children_c) == 0
    assert children == children_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genome_annotations_old():
    _log.info("Input {}".format(taxon_old))
    annotations = t_old.get_genome_annotations()
    _log.info("Output {}".format(annotations))
    assert isinstance(annotations, list) and len(annotations) == 1
    annotations_e = t_old_e.get_genome_annotations()
    assert isinstance(annotations_e, list) and len(annotations_e) == 1
    assert annotations[0].get_feature_ids() == annotations_e[0].get_feature_ids()
    annotations_c = t_client_old.get_genome_annotations()
    assert isinstance(annotations_c, list) and len(annotations_c) == 1
    # TODO check object reference string


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_scientific_lineage_old():
    _log.info("Input {}".format(taxon_old))
    scientific_lineage = t_old.get_scientific_lineage()
    _log.info("Output {}".format(scientific_lineage))
    assert isinstance(scientific_lineage, list) and len(scientific_lineage) > 0
    scientific_lineage_e = t_old_e.get_scientific_lineage()
    assert isinstance(scientific_lineage_e, list) and len(scientific_lineage_e) > 0
    assert scientific_lineage == scientific_lineage_e
    scientific_lineage_c = t_client_old.get_scientific_lineage()
    assert isinstance(scientific_lineage_c, list) and len(scientific_lineage_c) > 0
    assert scientific_lineage == scientific_lineage_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_scientific_name_old():
    _log.info("Input {}".format(taxon_old))
    scientific_name = t_old.get_scientific_name()
    _log.info("Output {}".format(scientific_name))
    assert isinstance(scientific_name, basestring) and len(scientific_name) > 0
    scientific_name_e = t_old_e.get_scientific_name()
    assert isinstance(scientific_name_e, basestring) and len(scientific_name_e) > 0
    assert scientific_name == scientific_name_e
    scientific_name_c = t_old_e.get_scientific_name()
    assert isinstance(scientific_name_c, basestring) and len(scientific_name_c) > 0
    assert scientific_name == scientific_name_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_taxonomic_id_old():
    try:
        _log.info("Input {}".format(taxon_old))
        taxonomic_id = t_old.get_taxonomic_id()
        _log.info("Output {}".format(taxonomic_id))
    except AttributeError:
        assert True
    else:
        assert False

    try:
        taxonomic_id_e = t_old_e.get_taxonomic_id()
    except AttributeError:
        assert True
    else:
        assert False

    try:
        taxonomic_id_c = t_client_old.get_taxonomic_id()
    except AttributeError:
        assert True
    else:
        assert False


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_kingdom_old():
    try:
        _log.info("Input {}".format(taxon_old))
        kingdom = t_old.get_kingdom()
        _log.info("Output {}".format(kingdom))
    except AttributeError:
        assert True
    else:
        assert False

    try:
        kingdom_e = t_old_e.get_kingdom()
    except AttributeError:
        assert True
    else:
        assert False

    try:
        kingdom_c = t_client_old.get_kingdom()
    except AttributeError:
        assert True
    else:
        assert False


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_domain_old():
    _log.info("Input {}".format(taxon_old))
    domain = t_old.get_domain()
    _log.info("Output {}".format(domain))
    assert isinstance(domain, basestring) and len(domain) > 0
    domain_e = t_old_e.get_domain()
    assert isinstance(domain_e, basestring) and len(domain_e) > 0
    assert domain == domain_e
    domain_c = t_client_old.get_domain()
    assert isinstance(domain_c, basestring) and len(domain_c) > 0
    assert domain == domain_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_aliases_old():
    _log.info("Input {}".format(taxon_old))
    aliases = t_old.get_aliases()
    _log.info("Output {}".format(aliases))
    assert isinstance(aliases, list) and len(aliases) == 0
    aliases_e = t_old_e.get_aliases()
    assert isinstance(aliases_e, list) and len(aliases_e) == 0
    assert aliases == aliases_e
    aliases_c = t_client_old.get_aliases()
    assert isinstance(aliases_c, list) and len(aliases_c) == 0
    assert aliases == aliases_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genetic_code_old():
    try:
        _log.info("Input {}".format(taxon_old))
        genetic_code = t_old.get_genetic_code()
        _log.info("Output {}".format(genetic_code))
        assert isinstance(genetic_code, int) and genetic_code != -1
    except AttributeError:
        assert False

    try:
        genetic_code_e = t_old_e.get_genetic_code()
        assert isinstance(genetic_code_e, int) and genetic_code_e != -1
    except AttributeError:
        assert False

    try:
        genetic_code_c = t_client_old.get_genetic_code()
        _log.info("Genetic code : {}".format(genetic_code_c))
        assert isinstance(genetic_code_c, int) and genetic_code_c != -1
    except AttributeError:
        assert False
