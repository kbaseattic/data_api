"""
Unit tests for genome_annotation
"""
import logging
from unittest import skipUnless

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from . import shared

from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.annotation.genome_annotation.api import _KBaseGenomes_Genome
from doekbase.data_api.annotation.genome_annotation.api import _GenomeAnnotation
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationClientAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api import exceptions

_log = logging.getLogger(__name__)

genome_new = "8020/39/1"
genome_old = "8020/41/1"
t_new = None
t_new_e = None
t_old = None
t_old_e = None
t_client_new = None
t_client_old = None
t_new_fid = None
t_new_contig_id = None
t_new_mrna_ids = []
t_new_cds_ids = []
t_new_gene_ids = []
t_old_fid = None
t_old_contig_id = None
t_old_mrna_ids = []
t_old_cds_ids = []
t_old_gene_ids = []

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

def fetch_new_feature_id(t_o):
    global t_new_fid

    if t_new_fid:
        return t_new_fid

    types = t_o.get_feature_types()
    core_types = ["gene", "mRNA", "CDS"]

    for ct in core_types:
        if ct in types:
            ftype = ct
            break
    else:
        ftype = types[0]

    t_new_fid = t_o.get_feature_ids(filters={"type_list": [ftype]})["by_type"][ftype][0]
    return t_new_fid


def fetch_new_contig_id(t_o):
    global t_new_contig_id

    if t_new_contig_id:
        return t_new_contig_id

    feature_id = fetch_new_feature_id(t_o)
    t_new_contig_id = t_o.get_feature_locations([feature_id])[feature_id][0]["contig_id"]
    return t_new_contig_id


def fetch_new_mrna_ids(t_o):
    global t_new_mrna_ids

    if t_new_mrna_ids:
        return t_new_mrna_ids

    t_new_mrna_ids = t_o.get_feature_ids(filters={"type_list": ["mRNA"]})["by_type"]["mRNA"][0:2]
    return t_new_mrna_ids


def fetch_new_cds_ids(t_o):
    global t_new_cds_ids

    if t_new_cds_ids:
        return t_new_cds_ids

    t_new_cds_ids = t_o.get_feature_ids(filters={"type_list": ["CDS"]})["by_type"]["CDS"][0:2]
    return t_new_cds_ids


def fetch_new_gene_ids(t_o):
    global t_new_gene_ids

    if t_new_gene_ids:
        return t_new_gene_ids

    t_new_gene_ids = t_o.get_feature_ids(filters={"type_list": ["gene"]})["by_type"]["gene"][0:2]
    return t_new_gene_ids


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
def test_get_feature_ids_invalid_filters_new():
    invalid_filters = {"invalid_key": ["kb_g.166819.mRNA.0"]}
    _log.debug("Input {} {}".format(genome_new, invalid_filters))
    for t_o in [t_new, t_new_e, t_client_new]:
        error_caught = False
        try:
            feature_ids_t_o = t_o.get_feature_ids(invalid_filters)
        except KeyError, e:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_invalid_groupby_new():
    invalid_groupby = "invalid_group"
    _log.debug("Input {} {}".format(genome_new, invalid_groupby))
    for t_o in [t_new, t_new_e, t_client_new]:
        error_caught = False
        try:
            feature_ids_t_o = t_o.get_feature_ids(group_by=invalid_groupby)
        except ValueError, e:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_filter_minus_strand_by_region_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        contig_id = fetch_new_contig_id(t_o)
        feature_ids_t_o = t_o.get_feature_ids(filters={
            "region_list": [{
                "contig_id": fetch_new_contig_id(t_o),
                "start": 1E9,
                "strand": "-",
                "length": 1E9
            }]
        },
        group_by="region")
        assert isinstance(feature_ids_t_o, dict)
        assert len(feature_ids_t_o["by_region"][contig_id]["-"]) > 0
        _log.debug("Output {}".format(len(feature_ids_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_filter_plus_strand_by_region_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        contig_id = fetch_new_contig_id(t_o)
        feature_ids_t_o = t_o.get_feature_ids(filters={
            "region_list": [{
                "contig_id": contig_id,
                "start": 0,
                "strand": "+",
                "length": 1E9
            }]
        },
        group_by="region")
        assert isinstance(feature_ids_t_o, dict)
        assert len(feature_ids_t_o["by_region"][contig_id]["+"]) > 0
        _log.debug("Output {}".format(len(feature_ids_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_subset_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_ids_t_o = t_o.get_feature_ids(filters={"type_list": ["mRNA"]})
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
def test_get_feature_locations_one_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_locations_t_o = t_o.get_feature_locations([fetch_new_feature_id(t_o)])
        _log.info(feature_locations_t_o)
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
def test_get_feature_dna_one_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_id = fetch_new_feature_id(t_o)
        feature_dna_t_o = t_o.get_feature_dna([feature_id])
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
def test_get_feature_functions_one_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_id = fetch_new_feature_id(t_o)
        feature_functions_t_o = t_o.get_feature_functions([feature_id])
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
def test_get_feature_aliases_one_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_id = fetch_new_feature_id(t_o)
        feature_aliases_t_o = t_o.get_feature_aliases([feature_id])
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
def test_get_feature_publications_one_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_id = fetch_new_feature_id(t_o)
        feature_publications_t_o = t_o.get_feature_publications([feature_id])
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
def test_get_features_one_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        feature_id = fetch_new_feature_id(t_o)
        features_t_o = t_o.get_features([feature_id])
        assert isinstance(features_t_o, dict)
        _log.debug("Output {}".format(len(features_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_proteins_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        proteins_t_o = t_o.get_proteins()
        assert isinstance(proteins_t_o, dict)
        assert len(proteins_t_o) > 0
        _log.debug("Output {}".format(len(proteins_t_o)))


def validate_utrs(utrs):
    for u in utrs:
        utr_dna_length = len(utrs[u]["utr_dna_sequence"])
        assert utrs[u]["utr_dna_sequence"] > 0

        assert utrs[u]["utr_locations"] > 0
        for loc in utrs[u]["utr_locations"]:
            assert loc["start"] > 0
            assert loc["strand"] == "+" or loc["strand"] == "-"
            assert loc["length"] > 0

        utr_location_sum = sum([z["length"] for z in utrs[u]["utr_locations"]])
        assert utr_location_sum == utr_dna_length


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_utrs_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        utrs_t_o = t_o.get_mrna_utrs()
        mrna_ids = t_o.get_feature_ids(filters={"type_list": ["mRNA"]})["by_type"]["mRNA"]
        mrna_locations = t_o.get_feature_locations(mrna_ids)
        cds_ids = t_o.get_cds_by_mrna(mrna_ids)
        cds_locations = t_o.get_feature_locations(cds_ids.values())

        for mrna_id in mrna_ids:
            num_mrna = len(mrna_locations[mrna_id])
            num_cds = len(cds_locations[cds_ids[mrna_id]])

            first_mrna = mrna_locations[mrna_id][0]
            first_cds = cds_locations[cds_ids[mrna_id]][0]
            last_mrna = mrna_locations[mrna_id][-1]
            last_cds = cds_locations[cds_ids[mrna_id]][-1]

            if num_mrna != num_cds:
                assert len(utrs_t_o[mrna_id]) > 0
                validate_utrs(utrs_t_o[mrna_id])
            elif (first_mrna["start"] < first_cds["start"]) or \
                 (last_mrna["start"] + last_mrna["length"] > last_cds["start"] + last_cds["length"]):
                assert len(utrs_t_o[mrna_id]) > 0
                validate_utrs(utrs_t_o[mrna_id])
            elif len(utrs_t_o[mrna_id]) > 0:
                validate_utrs(utrs_t_o[mrna_id])

        _log.debug("Output {}".format(len(utrs_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_utrs_one_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        mrna_id = fetch_new_mrna_ids(t_o)[0]
        _log.debug("Testing mRNA {}".format(mrna_id))
        utrs_t_o = t_o.get_mrna_utrs([mrna_id])
        mrna_locations = t_o.get_feature_locations([mrna_id])
        cds_ids = t_o.get_cds_by_mrna([mrna_id])
        cds_locations = t_o.get_feature_locations(cds_ids.values())

        if len(mrna_locations[mrna_id]) != len(cds_locations[cds_ids[mrna_id]]):
            assert len(utrs_t_o[mrna_id]) > 0
            validate_utrs(utrs_t_o[mrna_id])
        elif len(utrs_t_o[mrna_id]) > 0:
            validate_utrs(utrs_t_o[mrna_id])

        _log.debug("Output {}".format(len(utrs_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_exons_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        exons_t_o = t_o.get_mrna_exons()
        mrna_data = t_o.get_features(
            t_o.get_feature_ids(filters={"type_list": ["mRNA"]})["by_type"]["mRNA"])

        for mrna_id in mrna_data:
            dna = mrna_data[mrna_id]["feature_dna_sequence"]
            assert dna == "".join([x["exon_dna_sequence"] for x in exons_t_o[mrna_id]])

        _log.debug("Output {}".format(len(exons_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_exons_one_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        mrna_id = fetch_new_mrna_ids(t_o)[0]
        _log.debug("Testing mRNA {}".format(mrna_id))
        exons_t_o = t_o.get_mrna_exons([mrna_id])
        mrna_data = t_o.get_features([mrna_id])

        dna = mrna_data[mrna_id]["feature_dna_sequence"]
        assert dna == "".join([x["exon_dna_sequence"] for x in exons_t_o[mrna_id]])

        _log.debug("Output {}".format(len(exons_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_valid_new():
    for t_o in [t_new, t_new_e, t_client_new]:
        inputs = fetch_new_mrna_ids(t_o)
        _log.debug("Input {} {}".format(genome_new, inputs))
        cds_t_o = t_o.get_cds_by_mrna(inputs)
        assert len(cds_t_o) > 0
        _log.debug("Output {}".format(len(cds_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_invalid_new():
    inputs = ["kb_g.166819.mRNA.99999999999", "kb_g.166819.CDS.1"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        cds_t_o = t_o.get_cds_by_mrna(inputs)
        assert len(cds_t_o) == 0
        _log.debug("Output {}".format(len(cds_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_valid_new():
    for t_o in [t_new, t_new_e, t_client_new]:
        inputs = fetch_new_cds_ids(t_o)
        _log.debug("Input {} {}".format(genome_new, inputs))
        mrna_t_o = t_o.get_mrna_by_cds(inputs)
        assert len(mrna_t_o) > 0
        _log.debug("Output {}".format(len(mrna_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_invalid_new():
    inputs = ["kb_g.166819.mRNA.1", "kb_g.166819.CDS.9999999999"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        mrna_t_o = t_o.get_mrna_by_cds(inputs)
        assert len(mrna_t_o) == 0
        _log.debug("Output {}".format(len(mrna_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_valid_new():
    for t_o in [t_new, t_new_e, t_client_new]:
        inputs = fetch_new_mrna_ids(t_o)
        _log.debug("Input {} {}".format(genome_new, inputs))
        genes_t_o = t_o.get_gene_by_mrna(inputs)
        assert len(genes_t_o) > 0
        _log.debug("Output {}".format(len(genes_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_invalid_new():
    inputs = ["kb_g.166819.mRNA.99999999999", "kb_g.166819.CDS.1"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        genes_t_o = t_o.get_gene_by_mrna(inputs)
        assert len(genes_t_o) == 0
        _log.debug("Output {}".format(len(genes_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_valid_new():
    for t_o in [t_new, t_new_e, t_client_new]:
        inputs = fetch_new_gene_ids(t_o)
        _log.debug("Input {} {}".format(genome_new, inputs))
        cds_t_o = t_o.get_cds_by_gene(inputs)
        assert len(cds_t_o) > 0
        _log.debug("Output {}".format(len(cds_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_invalid_new():
    inputs = ["kb_g.166819.mRNA.1", "kb_g.166819.locus.999999"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        cds_t_o = t_o.get_cds_by_gene(inputs)
        assert len(cds_t_o) == 0
        _log.debug("Output {}".format(len(cds_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_valid_new():
    for t_o in [t_new, t_new_e, t_client_new]:
        inputs = fetch_new_gene_ids(t_o)
        _log.debug("Input {} {}".format(genome_new, inputs))
        mrna_t_o = t_o.get_mrna_by_gene(inputs)
        assert len(mrna_t_o) > 0
        _log.debug("Output {}".format(len(mrna_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_invalid_new():
    inputs = ["kb_g.166819.mRNA.1", "kb_g.166819.locus.999999"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        mrna_t_o = t_o.get_mrna_by_gene(inputs)
        assert len(mrna_t_o) == 0
        _log.debug("Output {}".format(len(mrna_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_valid_new():
    for t_o in [t_new, t_new_e, t_client_new]:
        inputs = fetch_new_cds_ids(t_o)
        _log.debug("Input {} {}".format(genome_new, inputs))
        genes_t_o = t_o.get_gene_by_cds(inputs)
        assert len(genes_t_o) > 0
        _log.debug("Output {}".format(len(genes_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_invalid_new():
    inputs = ["kb_g.166819.mRNA.1", "kb_g.166819.CDS.999999"]
    _log.debug("Input {} {}".format(genome_new, inputs))
    for t_o in [t_new, t_new_e, t_client_new]:
        genes_t_o = t_o.get_gene_by_cds(inputs)
        assert len(genes_t_o) == 0
        _log.debug("Output {}".format(len(genes_t_o)))


def validate_gff(s):
    lines = s.split('\n')

    for i in xrange(len(lines)):
        if lines[i].startswith("#"):
            continue

        tokens = lines[i].split('\t')

        assert len(tokens) == 9


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gff_valid_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e]:
        gff_t_o = t_o.get_gff()
        buf = StringIO.StringIO()
        gff_t_o.to_file(buf)
        gff = buf.getvalue()
        assert len(gff) > 0
        validate_gff(gff)
        _log.debug("Output {}".format(len(gff)))

    error_caught = False
    try:
        gff_t_o = t_client_new.get_gff()
    except NotImplementedError:
        error_caught = True

    assert error_caught


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_summary_new():
    # TODO fix this test, need to make sure the object references are correct in the test data
    return True

    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        _log.debug("get_referrers: {}".format(t_o.get_referrers()))
        summary_t_o = t_o.get_summary()
        _log.debug("Output {}".format(summary_t_o))
        assert "taxonomy" in summary_t_o
        assert "scientific_name" in summary_t_o["taxonomy"]
        assert "taxonomy_id" in summary_t_o["taxonomy"]
        assert "kingdom" in summary_t_o["taxonomy"]
        assert "scientific_lineage" in summary_t_o["taxonomy"]
        assert "genetic_code" in summary_t_o["taxonomy"]
        assert "organism_aliases" in summary_t_o["taxonomy"]

        assert "assembly" in summary_t_o
        assert "assembly_source" in summary_t_o["assembly"]
        assert "assembly_source_id" in summary_t_o["assembly"]
        assert "assembly_source_date" in summary_t_o["assembly"]
        assert "gc_content" in summary_t_o["assembly"]
        assert "dna_size" in summary_t_o["assembly"]
        assert "num_contigs" in summary_t_o["assembly"]
        assert "contig_ids" in summary_t_o["assembly"]

        assert "annotation" in summary_t_o
        assert "external_source" in summary_t_o["annotation"]
        assert "external_source_date" in summary_t_o["annotation"]
        assert "release" in summary_t_o["annotation"]
        assert "original_source_filename" in summary_t_o["annotation"]
        assert "feature_type_counts" in summary_t_o["annotation"]


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_save_summary_new():
    _log.debug("Input {}".format(genome_new))
    for t_o in [t_new, t_new_e, t_client_new]:
        saved = False
        saved = t_o.save_summary()
        assert saved


######## Old Genome Annotation Type tests

def fetch_old_feature_id(t_o):
    global t_old_fid

    if t_old_fid:
        return t_old_fid

    types = t_o.get_feature_types()
    core_types = ["gene", "mRNA", "CDS"]

    for ct in core_types:
        if ct in types:
            ftype = ct
            break
    else:
        ftype = types[0]

    t_old_fid = t_o.get_feature_ids(filters={"type_list": [ftype]})["by_type"][ftype][0]
    return t_old_fid


def fetch_old_contig_id(t_o):
    global t_old_contig_id

    if t_old_contig_id:
        return t_old_contig_id

    feature_id = fetch_old_feature_id(t_o)
    t_old_contig_id = t_o.get_feature_locations([feature_id])[feature_id][0]["contig_id"]
    return t_old_contig_id


def fetch_old_mrna_ids(t_o):
    global t_old_mrna_ids

    if t_old_mrna_ids:
        return t_old_mrna_ids

    t_old_mrna_ids = t_o.get_feature_ids(filters={"type_list": ["mRNA"]})["by_type"]["mRNA"][0:2]
    return t_old_mrna_ids


def fetch_old_cds_ids(t_o):
    global t_old_cds_ids

    if t_old_cds_ids:
        return t_old_cds_ids

    t_old_cds_ids = t_o.get_feature_ids(filters={"type_list": ["CDS"]})["by_type"]["CDS"][0:2]
    return t_old_cds_ids


def fetch_old_gene_ids(t_o):
    global t_old_gene_ids

    if t_old_gene_ids:
        return t_old_gene_ids

    t_old_gene_ids = t_o.get_feature_ids(filters={"type_list": ["gene"]})["by_type"]["gene"][0:2]
    return t_old_gene_ids


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
def test_get_feature_ids_subset_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_ids_t_o = t_o.get_feature_ids(filters={"type_list": ["mRNA"]})
        assert isinstance(feature_ids_t_o, dict)
        _log.debug("Output {}".format(type(feature_ids_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_invalid_filters_old():
    invalid_filters = {"invalid_key": ["kb_g.166819.mRNA.0"]}
    _log.debug("Input {} {}".format(genome_old, invalid_filters))
    for t_o in [t_old, t_old_e, t_client_old]:
        error_caught = False
        try:
            feature_ids_t_o = t_o.get_feature_ids(invalid_filters)
        except KeyError, e:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_invalid_groupby_old():
    invalid_groupby = "invalid_group"
    _log.debug("Input {} {}".format(genome_old, invalid_groupby))
    for t_o in [t_old, t_old_e, t_client_old]:
        error_caught = False
        try:
            feature_ids_t_o = t_o.get_feature_ids(group_by=invalid_groupby)
        except ValueError, e:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_filter_minus_strand_by_region_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        contig_id = fetch_old_contig_id(t_o)
        feature_ids_t_o = t_o.get_feature_ids(filters={
            "region_list": [{
                "contig_id": contig_id,
                "start": 1E9,
                "strand": "-",
                "length": 1E9
            }]
        },
        group_by="region")
        assert isinstance(feature_ids_t_o, dict)
        assert len(feature_ids_t_o["by_region"][contig_id]["-"]) > 0
        _log.debug("Output {}".format(len(feature_ids_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_ids_filter_plus_strand_by_region_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        contig_id = fetch_old_contig_id(t_o)
        feature_ids_t_o = t_o.get_feature_ids(filters={
            "region_list": [{
                "contig_id": contig_id,
                "start": 0,
                "strand": "+",
                "length": 1E9
            }]
        },
        group_by="region")
        assert isinstance(feature_ids_t_o, dict)
        assert len(feature_ids_t_o["by_region"][contig_id]["+"]) > 0
        _log.debug("Output {}".format(len(feature_ids_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_counts_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_type_counts_t_o = t_o.get_feature_type_counts()
        assert isinstance(feature_type_counts_t_o, dict)
        _log.debug("Output {}".format(feature_type_counts_t_o))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_type_counts_one_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_type_counts_t_o = t_o.get_feature_type_counts(["mRNA"])
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
def test_get_feature_locations_one_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_id = fetch_old_feature_id(t_o)
        feature_locations_t_o = t_o.get_feature_locations([feature_id])
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
def test_get_feature_dna_one_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_id = fetch_old_feature_id(t_o)
        feature_dna_t_o = t_o.get_feature_dna([feature_id])
        assert isinstance(feature_dna_t_o, dict)
        _log.debug("Output {}".format(len(feature_dna_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_functions_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_functions_t_o = t_o.get_feature_functions()
        assert isinstance(feature_functions_t_o, dict)
        _log.debug("Output {}".format(len(feature_functions_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_feature_functions_one_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_id = fetch_old_feature_id(t_o)
        feature_functions_t_o = t_o.get_feature_functions([feature_id])
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
def test_get_feature_aliases_one_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_id = fetch_old_feature_id(t_o)
        feature_aliases_t_o = t_o.get_feature_aliases([feature_id])
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
def test_get_feature_publications_one_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_id = fetch_old_feature_id(t_o)
        feature_publications_t_o = t_o.get_feature_publications([feature_id])
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
def test_get_features_one_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        feature_id = fetch_old_feature_id(t_o)
        features_t_o = t_o.get_features([feature_id])
        assert isinstance(features_t_o, dict)
        _log.debug("Output {}".format(len(features_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_proteins_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        proteins_t_o = t_o.get_proteins()
        assert isinstance(proteins_t_o, dict)
        assert len(proteins_t_o) > 0
        _log.debug("Output {}".format(len(proteins_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_utrs_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        error_caught = False
        try:
            utrs_t_o = t_o.get_mrna_utrs()
        except TypeError:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_exons_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        exons_t_o = t_o.get_mrna_exons()
        mrna_data = t_o.get_features(
            t_o.get_feature_ids(filters={"type_list": ["mRNA"]})["by_type"]["mRNA"])

        for mrna_id in mrna_data:
            dna = mrna_data[mrna_id]["feature_dna_sequence"]
            assert dna == "".join([x["exon_dna_sequence"] for x in exons_t_o[mrna_id]])

        _log.debug("Output {}".format(len(exons_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_exons_one_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        mrna_id = t_o.get_feature_ids(filters={"type_list": ["mRNA"]})["by_type"]["mRNA"][0]
        exons_t_o = t_o.get_mrna_exons([mrna_id])
        mrna_data = t_o.get_features([mrna_id])

        dna = mrna_data[mrna_id]["feature_dna_sequence"]
        assert dna == "".join([x["exon_dna_sequence"] for x in exons_t_o[mrna_id]])

        _log.debug("Output {}".format(len(exons_t_o)))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_mrna_old():
    for t_o in [t_old, t_old_e, t_client_old]:
        inputs = fetch_old_mrna_ids(t_o)
        _log.debug("Input {} {}".format(genome_old, inputs))
        error_caught = False
        try:
            cds_t_o = t_o.get_cds_by_mrna(inputs)
        except TypeError:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_cds_old():
    for t_o in [t_old, t_old_e, t_client_old]:
        inputs = fetch_old_cds_ids(t_o)
        _log.debug("Input {} {}".format(genome_old, inputs))
        error_caught = False
        try:
            mrna_t_o = t_o.get_mrna_by_cds(inputs)
        except TypeError:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_mrna_old():
    for t_o in [t_old, t_old_e, t_client_old]:
        inputs = fetch_old_mrna_ids(t_o)
        _log.debug("Input {} {}".format(genome_old, inputs))
        error_caught = False
        try:
            genes_t_o = t_o.get_gene_by_mrna(inputs)
        except TypeError:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_cds_by_gene_old():
    for t_o in [t_old, t_old_e, t_client_old]:
        inputs = fetch_old_gene_ids(t_o)
        _log.debug("Input {} {}".format(genome_old, inputs))
        error_caught = False
        try:
            cds_t_o = t_o.get_cds_by_gene(inputs)
        except TypeError:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_mrna_by_gene_old():
    for t_o in [t_old, t_old_e, t_client_old]:
        inputs = fetch_old_gene_ids(t_o)
        _log.debug("Input {} {}".format(genome_old, inputs))
        error_caught = False
        try:
            mrna_t_o = t_o.get_mrna_by_gene(inputs)
        except TypeError:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gene_by_cds_old():
    for t_o in [t_old, t_old_e, t_client_old]:
        inputs = fetch_old_cds_ids(t_o)
        _log.debug("Input {} {}".format(genome_old, inputs))
        error_caught = False
        try:
            genes_t_o = t_o.get_gene_by_cds(inputs)
        except TypeError:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gff_valid_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e]:
        gff_t_o = t_o.get_gff()
        buf = StringIO.StringIO()
        gff_t_o.to_file(buf)
        gff = buf.getvalue()
        assert len(gff) > 0
        validate_gff(gff)
        _log.debug("Output {}".format(len(gff)))

    error_caught = False
    try:
        gff_t_o = t_client_old.get_gff()
    except NotImplementedError:
        error_caught = True

    assert error_caught
    _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_summary_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        error_caught = False
        try:
            summary_t_o = t_o.get_summary()
        except TypeError:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_save_summary_old():
    _log.debug("Input {}".format(genome_old))
    for t_o in [t_old, t_old_e, t_client_old]:
        error_caught = False
        try:
            saved = t_o.save_summary()
        except TypeError:
            error_caught = True

        assert error_caught
        _log.debug("Output {}".format(error_caught))
