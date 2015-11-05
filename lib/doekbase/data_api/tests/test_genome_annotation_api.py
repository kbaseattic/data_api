"""
Unit tests for genome_annotation
"""
import logging
from unittest import skipUnless

from . import shared
from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI

_log = logging.getLogger(__name__)

genome_new = "PrototypeReferenceGenomes/kb|g.166819"
genome_old = "OriginalReferenceGenomes/kb|g.166819"
t_new = None
t_old = None

def setup():
    shared.setup()
    global t_new, t_old
    t_new = GenomeAnnotationAPI(shared.services, shared.token, genome_new)
    t_old = GenomeAnnotationAPI(shared.services, shared.token, genome_old)

######## New Genome type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_taxon_new():
    _log.info("Input {}".format(genome_new))
    taxon = t_new.get_taxon()
    _log.info("Output {}".format(taxon))
    assert isinstance(taxon, TaxonAPI)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_assembly_new():
    _log.info("Input {}".format(genome_new))
    assembly = t_new.get_assembly()
    _log.info("Output {}".format(assembly))
    assert isinstance(assembly, AssemblyAPI)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_types_new():
    _log.info("Input {}".format(genome_new))
    feature_types = t_new.get_feature_types()
    _log.info("Output {}".format(feature_types))
    assert isinstance(feature_types, list)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_descriptions_new():
    _log.info("Input {}".format(genome_new))
    feature_type_descriptions = t_new.get_feature_type_descriptions()
    _log.info("Output {}".format(feature_type_descriptions))
    assert isinstance(feature_type_descriptions, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_new():
    _log.info("Input {}".format(genome_new))
    feature_ids = t_new.get_feature_ids()
    _log.info("Output {}".format(type(feature_ids)))
    assert isinstance(feature_ids, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_counts_new():
    _log.info("Input {}".format(genome_new))
    feature_type_counts = t_new.get_feature_type_counts()
    _log.info("Output {}".format(feature_type_counts))
    assert isinstance(feature_type_counts, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_locations_new():
    _log.info("Input {}".format(genome_new))
    feature_locations = t_new.get_feature_locations()
    _log.info("Output {}".format(len(feature_locations)))
    assert isinstance(feature_locations, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_dna_new():
    _log.info("Input {}".format(genome_new))
    feature_dna = t_new.get_feature_dna()
    _log.info("Output {}".format(len(feature_dna)))
    assert isinstance(feature_dna, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_functions_new():
    _log.info("Input {}".format(genome_new))
    feature_functions = t_new.get_feature_functions()
    _log.info("Output {}".format(len(feature_functions)))
    assert isinstance(feature_functions, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_aliases_new():
    _log.info("Input {}".format(genome_new))
    feature_aliases = t_new.get_feature_aliases()
    _log.info("Output {}".format(len(feature_aliases)))
    assert isinstance(feature_aliases, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_publications_new():
    _log.info("Input {}".format(genome_new))
    feature_publications = t_new.get_feature_publications()
    _log.info("Output {}".format(len(feature_publications)))
    assert isinstance(feature_publications, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_features_new():
    _log.info("Input {}".format(genome_new))
    features = t_new.get_features()
    _log.info("Output {}".format(len(features)))
    assert isinstance(features, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_proteins_new():
    _log.info("Input {}".format(genome_new))
    proteins = t_new.get_proteins()
    _log.info("Output {}".format(len(proteins)))
    assert isinstance(proteins, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_valid_new():
    inputs = ["kb|g.166819.mRNA.0", "kb|g.166819.mRNA.238"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_cds_by_mrna(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 2


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_invalid_new():
    inputs = ["kb|g.166819.mRNA.99999999999", "kb|g.166819.CDS.1"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_cds_by_mrna(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_valid_new():
    inputs = ["kb|g.166819.CDS.0", "kb|g.166819.CDS.278"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_mrna_by_cds(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 2


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_invalid_new():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.CDS.9999999999"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_mrna_by_cds(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_valid_new():
    inputs = ["kb|g.166819.mRNA.0", "kb|g.166819.mRNA.238"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_gene_by_mrna(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 2


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_invalid_new():
    inputs = ["kb|g.166819.mRNA.99999999999", "kb|g.166819.CDS.1"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_gene_by_mrna(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_valid_new():
    inputs = ["kb|g.166819.locus.256", "kb|g.166819.locus.112"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_cds_by_gene(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 2


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_invalid_new():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.locus.999999"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_cds_by_gene(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_valid_new():
    inputs = ["kb|g.166819.locus.256", "kb|g.166819.locus.112"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_mrna_by_gene(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 2


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_invalid_new():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.locus.999999"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_mrna_by_gene(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_valid_new():
    inputs = ["kb|g.166819.CDS.0", "kb|g.166819.CDS.278"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_gene_by_cds(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 2


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_invalid_new():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.CDS.999999"]
    _log.info("Input {} {}".format(genome_new, inputs))
    subset_features = t_new.get_gene_by_cds(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


######## Old Genome Annotation Type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_taxon_old():
    _log.info("Input {}".format(genome_old))
    taxon = t_old.get_taxon()
    _log.info("Output {}".format(taxon))
    assert isinstance(taxon, TaxonAPI)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_assembly_old():
    _log.info("Input {}".format(genome_old))
    assembly = t_old.get_assembly()
    _log.info("Output {}".format(assembly))
    assert isinstance(assembly, AssemblyAPI)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_types_old():
    _log.info("Input {}".format(genome_old))
    feature_types = t_old.get_feature_types()
    _log.info("Output {}".format(feature_types))
    assert isinstance(feature_types, list)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_descriptions_old():
    _log.info("Input {}".format(genome_old))
    feature_type_descriptions = t_old.get_feature_type_descriptions()
    _log.info("Output {}".format(feature_type_descriptions))
    assert isinstance(feature_type_descriptions, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_old():
    _log.info("Input {}".format(genome_old))
    feature_ids = t_old.get_feature_ids()
    _log.info("Output {}".format(type(feature_ids)))
    assert isinstance(feature_ids, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_counts_old():
    _log.info("Input {}".format(genome_old))
    feature_type_counts = t_old.get_feature_type_counts()
    _log.info("Output {}".format(feature_type_counts))
    assert isinstance(feature_type_counts, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_locations_old():
    _log.info("Input {}".format(genome_old))
    feature_locations = t_old.get_feature_locations()
    _log.info("Output {}".format(len(feature_locations)))
    assert isinstance(feature_locations, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_dna_old():
    _log.info("Input {}".format(genome_old))
    feature_dna = t_old.get_feature_dna()
    _log.info("Output {}".format(len(feature_dna)))
    assert isinstance(feature_dna, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_functions_old():
    _log.info("Input {}".format(genome_old))
    feature_functions = t_old.get_feature_functions()
    _log.info("Output {}".format(len(feature_functions)))
    assert isinstance(feature_functions, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_aliases_old():
    _log.info("Input {}".format(genome_old))
    feature_aliases = t_old.get_feature_aliases()
    _log.info("Output {}".format(len(feature_aliases)))
    assert isinstance(feature_aliases, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_publications_old():
    _log.info("Input {}".format(genome_old))
    feature_publications = t_old.get_feature_publications()
    _log.info("Output {}".format(len(feature_publications)))
    assert isinstance(feature_publications, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_features_old():
    _log.info("Input {}".format(genome_old))
    features = t_old.get_features()
    _log.info("Output {}".format(len(features)))
    assert isinstance(features, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_proteins_old():
    _log.info("Input {}".format(genome_old))
    proteins = t_old.get_proteins()
    _log.info("Output {}".format(len(proteins)))
    assert isinstance(proteins, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_valid_old():
    inputs = ["kb|g.166819.mRNA.0", "kb|g.166819.mRNA.238"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_cds_by_mrna(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_invalid_old():
    inputs = ["kb|g.166819.mRNA.99999999999", "kb|g.166819.CDS.1"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_cds_by_mrna(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_valid_old():
    inputs = ["kb|g.166819.CDS.0", "kb|g.166819.CDS.278"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_mrna_by_cds(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_invalid_old():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.CDS.9999999999"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_mrna_by_cds(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_valid_old():
    inputs = ["kb|g.166819.mRNA.0", "kb|g.166819.mRNA.238"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_gene_by_mrna(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_invalid_old():
    inputs = ["kb|g.166819.mRNA.99999999999", "kb|g.166819.CDS.1"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_gene_by_mrna(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_valid_old():
    inputs = ["kb|g.166819.locus.256", "kb|g.166819.locus.112"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_cds_by_gene(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_invalid_old():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.locus.999999"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_cds_by_gene(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_valid_old():
    inputs = ["kb|g.166819.locus.256", "kb|g.166819.locus.112"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_mrna_by_gene(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_invalid_old():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.locus.999999"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_mrna_by_gene(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_valid_old():
    inputs = ["kb|g.166819.CDS.0", "kb|g.166819.CDS.278"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_gene_by_cds(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_invalid_old():
    inputs = ["kb|g.166819.mRNA.1", "kb|g.166819.CDS.999999"]
    _log.info("Input {} {}".format(genome_old, inputs))
    subset_features = t_old.get_gene_by_cds(inputs)
    _log.info("Output {}".format(subset_features))
    assert len(subset_features) == 0
