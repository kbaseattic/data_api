"""
Unit tests for genome_annotation
"""
import logging
from unittest import skipUnless

from . import shared

from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.annotation.genome_annotation.api import _KBaseGenomes_Genome
from doekbase.data_api.annotation.genome_annotation.api import _GenomeAnnotation
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationClientAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI

_log = logging.getLogger(__name__)

genome_new = "ReferenceGenomeAnnotations/kb|g.166819"
genome_old = "OriginalReferenceGenomes/kb|g.166819"
t_new = None
t_new_e = None
t_old = None
t_old_e = None
t_client_new = None
t_client_old = None

def setup():
    shared.setup()
    global t_new, t_new_e, t_old, t_old_e, t_client_new, t_client_old
    t_new = GenomeAnnotationAPI(shared.services, shared.token, genome_new)
    t_new_e = _GenomeAnnotation(shared.services, shared.token, genome_new)
    t_old = GenomeAnnotationAPI(shared.services, shared.token, genome_old)
    t_old_e = _KBaseGenomes_Genome(shared.services, shared.token, genome_old)
    t_client_new = GenomeAnnotationClientAPI(shared.services["genome_annotation_service_url"], shared.token, genome_new)
    t_client_old = GenomeAnnotationClientAPI(shared.services["genome_annotation_service_url"], shared.token, genome_old)

######## New Genome type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_taxon_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e]:
        taxon_t_o = t_o.get_taxon()
        assert isinstance(taxon_t_o, TaxonAPI)
        _log.debug("Output {}".format(taxon_t_o))

    taxon_c_new = t_client_new.get_taxon()
    assert taxon_c_new is not None


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_assembly_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e]:
        assembly_t_o = t_o.get_assembly()
        assert isinstance(assembly_t_o, AssemblyAPI)
        _log.debug("Output {}".format(assembly_t_o))

    assembly_c_new = t_client_new.get_assembly()
    assert assembly_c_new is not None


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_types_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_types_t_o = t_o.get_feature_types()
        assert isinstance(feature_types_t_o, list)
        _log.debug("Output {}".format(len(feature_types_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_descriptions_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_type_descriptions_t_o = t_o.get_feature_type_descriptions()
        assert isinstance(feature_type_descriptions_t_o, dict)
        _log.debug("Output {}".format(len(feature_type_descriptions_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_ids_t_o = t_o.get_feature_ids()
        assert isinstance(feature_ids_t_o, dict)
        _log.debug("Output {}".format(len(feature_ids_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_counts_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_type_counts_t_o = t_o.get_feature_type_counts()
        assert isinstance(feature_type_counts_t_o, dict)
        _log.debug("Output {}".format(len(feature_type_counts_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_locations_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_locations_t_o = t_o.get_feature_locations()
        assert isinstance(feature_locations_t_o, dict)
        _log.debug("Output {}".format(len(feature_locations_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_dna_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_dna_t_o = t_o.get_feature_dna()
        assert isinstance(feature_dna_t_o, dict)
        _log.debug("Output {}".format(len(feature_dna_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_functions_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_functions_t_o = t_o.get_feature_functions()
        assert isinstance(feature_functions_t_o, dict)
        _log.debug("Output {}".format(len(feature_functions_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_aliases_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_aliases_t_o = t_o.get_feature_aliases()
        assert isinstance(feature_aliases_t_o, dict)
        _log.debug("Output {}".format(len(feature_aliases_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_publications_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_publications_t_o = t_o.get_feature_publications()
        assert isinstance(feature_publications_t_o, dict)
        _log.debug("Output {}".format(len(feature_publications_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_features_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        features_t_o = t_o.get_features()
        assert isinstance(features_t_o, dict)
        _log.debug("Output {}".format(len(features_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_proteins_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        proteins_t_o = t_o.get_proteins()
        assert isinstance(proteins_t_o, dict)
        _log.debug("Output {}".format(len(proteins_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_valid_new():
    inputs = ["kb|g.166819.mRNA.0", "kb|g.166819.mRNA.238"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        cds_t_o = t_o.get_cds_by_mrna(inputs)
        assert len(cds_t_o) == 2
        _log.debug("Output {}".format(cds_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_invalid_new():
    inputs = ["kb|g.166819.mRNA.99999999999", "kb|g.166819.CDS.1"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        cds_t_o = t_o.get_cds_by_mrna(inputs)
        assert len(cds_t_o) == 0
        _log.debug("Output {}".format(cds_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_valid_new():
    inputs = ["kb|g.166819.CDS.0", "kb|g.166819.CDS.278"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        mrna_t_o = t_o.get_mrna_by_cds(inputs)
        assert len(mrna_t_o) == 2
        _log.debug("Output {}".format(mrna_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_invalid_new():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.CDS.9999999999"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        mrna_t_o = t_o.get_mrna_by_cds(inputs)
        assert len(mrna_t_o) == 0
        _log.debug("Output {}".format(mrna_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_valid_new():
    inputs = ["kb|g.166819.mRNA.0", "kb|g.166819.mRNA.238"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        genes_t_o = t_o.get_gene_by_mrna(inputs)
        assert len(genes_t_o) == 2
        _log.debug("Output {}".format(genes_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_invalid_new():
    inputs = ["kb|g.166819.mRNA.99999999999", "kb|g.166819.CDS.1"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        genes_t_o = t_o.get_gene_by_mrna(inputs)
        assert len(genes_t_o) == 0
        _log.debug("Output {}".format(genes_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_valid_new():
    inputs = ["kb|g.166819.locus.256", "kb|g.166819.locus.112"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        cds_t_o = t_o.get_cds_by_gene(inputs)
        assert len(cds_t_o) == 2
        _log.debug("Output {}".format(cds_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_invalid_new():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.locus.999999"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        cds_t_o = t_o.get_cds_by_gene(inputs)
        assert len(cds_t_o) == 0
        _log.debug("Output {}".format(cds_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_valid_new():
    inputs = ["kb|g.166819.locus.256", "kb|g.166819.locus.112"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        mrna_t_o = t_o.get_mrna_by_gene(inputs)
        assert len(mrna_t_o) == 2
        _log.debug("Output {}".format(mrna_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_invalid_new():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.locus.999999"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        mrna_t_o = t_o.get_mrna_by_gene(inputs)
        assert len(mrna_t_o) == 0
        _log.debug("Output {}".format(mrna_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_valid_new():
    inputs = ["kb|g.166819.CDS.0", "kb|g.166819.CDS.278"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        genes_t_o = t_o.get_gene_by_cds(inputs)
        assert len(genes_t_o) == 2
        _log.debug("Output {}".format(genes_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_invalid_new():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.CDS.999999"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        genes_t_o = t_o.get_gene_by_cds(inputs)
        assert len(genes_t_o) == 0
        _log.debug("Output {}".format(genes_t_o))


######## Old Genome Annotation Type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_taxon_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e]:
        taxon_t_o = t_o.get_taxon()
        assert isinstance(taxon_t_o, TaxonAPI)
        _log.debug("Output {}".format(taxon_t_o))

    taxon_c_old = t_client_old.get_taxon()
    assert taxon_c_old is not None
    _log.debug("Output {}".format(taxon_c_old))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_assembly_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e]:
        assembly_t_o = t_o.get_assembly()
        assert isinstance(assembly_t_o, AssemblyAPI)
        _log.debug("Output {}".format(assembly_t_o))

    assembly_c_old = t_client_old.get_assembly()
    assert assembly_c_old is not None
    _log.debug("Output {}".format(assembly_c_old))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_types_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_types_t_o = t_o.get_feature_types()
        assert isinstance(feature_types_t_o, list)
        _log.debug("Output {}".format(feature_types_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_descriptions_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_type_descriptions_t_o = t_o.get_feature_type_descriptions()
        assert isinstance(feature_type_descriptions_t_o, dict)
        _log.debug("Output {}".format(feature_type_descriptions_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_ids_t_o = t_o.get_feature_ids()
        assert isinstance(feature_ids_t_o, dict)
        _log.debug("Output {}".format(type(feature_ids_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_counts_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_type_counts_t_o = t_o.get_feature_type_counts()
        assert isinstance(feature_type_counts_t_o, dict)
        _log.debug("Output {}".format(feature_type_counts_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_locations_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_locations_t_o = t_o.get_feature_locations()
        assert isinstance(feature_locations_t_o, dict)
        _log.debug("Output {}".format(len(feature_locations_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_dna_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_dna_t_o = t_o.get_feature_dna()
        assert isinstance(feature_dna_t_o, dict)
        _log.debug("Output {}".format(len(feature_dna_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_functions_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_new_e, t_old, t_old_e, t_client_new, t_client_old]:
        feature_functions_t_o = t_o.get_feature_functions()
        assert isinstance(feature_functions_t_o, dict)
        _log.debug("Output {}".format(len(feature_functions_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_aliases_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_aliases_t_o = t_o.get_feature_aliases()
        assert isinstance(feature_aliases_t_o, dict)
        _log.debug("Output {}".format(len(feature_aliases_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_publications_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_publications_t_o = t_o.get_feature_publications()
        assert isinstance(feature_publications_t_o, dict)
        _log.debug("Output {}".format(len(feature_publications_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_features_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        features_t_o = t_o.get_features()
        assert isinstance(features_t_o, dict)
        _log.debug("Output {}".format(len(features_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_proteins_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        proteins_t_o = t_o.get_proteins()
        assert isinstance(proteins_t_o, dict)
        _log.debug("Output {}".format(len(proteins_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_valid_old():
    inputs = ["kb|g.166819.mRNA.0", "kb|g.166819.mRNA.238"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        cds_t_o = t_o.get_cds_by_mrna(inputs)
        assert len(cds_t_o) == 0
        _log.debug("Output {}".format(cds_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_invalid_old():
    inputs = ["kb|g.166819.mRNA.99999999999", "kb|g.166819.CDS.1"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        cds_t_o = t_o.get_cds_by_mrna(inputs)
        assert len(cds_t_o) == 0
        _log.debug("Output {}".format(cds_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_valid_old():
    inputs = ["kb|g.166819.CDS.0", "kb|g.166819.CDS.278"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        mrna_t_o = t_o.get_mrna_by_cds(inputs)
        assert len(mrna_t_o) == 0
        _log.debug("Output {}".format(mrna_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_invalid_old():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.CDS.9999999999"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        mrna_t_o = t_o.get_mrna_by_cds(inputs)
        assert len(mrna_t_o) == 0
        _log.debug("Output {}".format(mrna_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_valid_old():
    inputs = ["kb|g.166819.mRNA.0", "kb|g.166819.mRNA.238"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        genes_t_o = t_o.get_gene_by_mrna(inputs)
        assert len(genes_t_o) == 0
        _log.debug("Output {}".format(genes_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_invalid_old():
    inputs = ["kb|g.166819.mRNA.99999999999", "kb|g.166819.CDS.1"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        genes_t_o = t_o.get_gene_by_mrna(inputs)
        assert len(genes_t_o) == 0
        _log.debug("Output {}".format(genes_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_valid_old():
    inputs = ["kb|g.166819.locus.256", "kb|g.166819.locus.112"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        cds_t_o = t_o.get_cds_by_gene(inputs)
        assert len(cds_t_o) == 0
        _log.debug("Output {}".format(cds_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_invalid_old():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.locus.999999"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        cds_t_o = t_o.get_cds_by_gene(inputs)
        assert len(cds_t_o) == 0
        _log.debug("Output {}".format(cds_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_valid_old():
    inputs = ["kb|g.166819.locus.256", "kb|g.166819.locus.112"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        mrna_t_o = t_o.get_mrna_by_gene(inputs)
        assert len(mrna_t_o) == 0
        _log.debug("Output {}".format(mrna_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_invalid_old():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.locus.999999"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        mrna_t_o = t_o.get_mrna_by_gene(inputs)
        assert len(mrna_t_o) == 0
        _log.debug("Output {}".format(mrna_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_valid_old():
    inputs = ["kb|g.166819.CDS.0", "kb|g.166819.CDS.278"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        genes_t_o = t_o.get_gene_by_cds(inputs)
        assert len(genes_t_o) == 0
        _log.debug("Output {}".format(genes_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_invalid_old():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.CDS.999999"]
    _log.debug("Input {} {}".format(genome_old, inputs))
    for t_o in [t_old, t_old_e, t_client_old]:
        genes_t_o = t_o.get_gene_by_cds(inputs)
        assert len(genes_t_o) == 0
        _log.debug("Output {}".format(genes_t_o))
