"""
Unit tests for assembly
"""
import logging
from unittest import skipUnless

from . import shared

from doekbase.data_api.sequence.assembly import AssemblyAPI
from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI

_log = logging.getLogger(__name__)

assembly_new = "PrototypeReferenceGenomes/kb|g.3157_assembly"
assembly_old = "OriginalReferenceGenomes/kb|g.3157.contigset"


def setup():
    shared.setup()


###### New Assembly Type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_assembly_id_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    assembly_id = t.get_assembly_id()
    _log.info("Output {}".format(assembly_id))
    assert isinstance(assembly_id, basestring) and len(assembly_id) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genome_annotations_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    annotations = t.get_genome_annotations()
    _log.info("Output {}".format(annotations))
    assert isinstance(annotations, list) and \
        len([True for x in annotations if isinstance(x, GenomeAnnotationAPI)]) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_external_source_info_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    info = t.get_external_source_info()
    _log.info("Output {}".format(info))
    assert isinstance(info, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_stats_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    stats = t.get_stats()
    _log.info("Output {}".format(stats))
    assert isinstance(stats, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_number_contigs_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    count = t.get_number_contigs()
    _log.info("Output {}".format(count))
    assert isinstance(count, int) and count > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gc_content_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    gc_content = t.get_gc_content()
    _log.info("Output {}".format(gc_content))
    assert isinstance(gc_content, float) and gc_content > 0.1


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_dna_size_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    dna_size = t.get_dna_size()
    _log.info("Output {}".format(dna_size))
    assert isinstance(dna_size, int) and dna_size > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_lengths_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    contig_lengths = t.get_contig_lengths()
    _log.info("Output {}".format(contig_lengths))
    assert isinstance(contig_lengths, dict) and len(contig_lengths) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_gc_content_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    contig_gc_content = t.get_contig_gc_content()
    _log.info("Output {}".format(contig_gc_content))
    assert isinstance(contig_gc_content, dict) and len(contig_gc_content) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_ids_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    contig_ids = t.get_contig_ids()
    _log.info("Output {}".format(contig_ids))
    assert isinstance(contig_ids, list) and len(contig_ids) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contigs_new():
    _log.info("Input {}".format(assembly_new))
    t = AssemblyAPI(shared.services, shared.token, assembly_new)
    contigs = t.get_contigs()
    _log.info("Output {}".format(contigs))
    assert isinstance(contigs, dict) and len(contigs) > 0


###### Old Assembly Type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_assembly_id_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    assembly_id = t.get_assembly_id()
    _log.info("Output {}".format(assembly_id))
    assert isinstance(assembly_id, basestring) and len(assembly_id) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genome_annotations_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    annotations = t.get_genome_annotations()
    _log.info("Output {}".format(annotations))
    assert isinstance(annotations, list) and \
        len([True for x in annotations if isinstance(x, GenomeAnnotationAPI)]) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_external_source_info_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    info = t.get_external_source_info()
    _log.info("Output {}".format(info))
    assert isinstance(info, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_stats_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    stats = t.get_stats()
    _log.info("Output {}".format(stats))
    assert isinstance(stats, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_number_contigs_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    count = t.get_number_contigs()
    _log.info("Output {}".format(count))
    assert isinstance(count, int) and count > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gc_content_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    gc_content = t.get_gc_content()
    _log.info("Output {}".format(gc_content))
    assert isinstance(gc_content, float) and gc_content > 0.1


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_dna_size_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    dna_size = t.get_dna_size()
    _log.info("Output {}".format(dna_size))
    assert isinstance(dna_size, int) and dna_size > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_lengths_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    contig_lengths = t.get_contig_lengths()
    _log.info("Output {}".format(contig_lengths))
    assert isinstance(contig_lengths, dict) and len(contig_lengths) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_gc_content_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    contig_gc_content = t.get_contig_gc_content()
    _log.info("Output {}".format(contig_gc_content))
    assert isinstance(contig_gc_content, dict) and len(contig_gc_content) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_ids_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    contig_ids = t.get_contig_ids()
    _log.info("Output {}".format(contig_ids))
    assert isinstance(contig_ids, list) and len(contig_ids) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contigs_old():
    _log.info("Input {}".format(assembly_old))
    t = AssemblyAPI(shared.services, shared.token, assembly_old)
    contigs = t.get_contigs()
    _log.info("Output {}".format(contigs))
    assert isinstance(contigs, dict) and len(contigs) > 0