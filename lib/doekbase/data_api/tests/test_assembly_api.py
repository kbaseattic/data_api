"""
Unit tests for assembly
"""
import logging
from unittest import skipUnless

from . import shared
from doekbase.data_api import exceptions
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.sequence.assembly.api import AssemblyClientAPI
from doekbase.data_api.sequence.assembly.api import _KBaseGenomes_ContigSet
from doekbase.data_api.sequence.assembly.api import _Assembly

_log = logging.getLogger(__name__)

assembly_new = "ReferenceGenomeAnnotations/kb|g.166819_assembly"
assembly_old = "OriginalReferenceGenomes/kb|g.166819.contigset"
t_new = None
t_new_e = None
t_old = None
t_old_e = None
t_client_old = None
t_client_new = None
g_skip_shock = False

def setup():
    shared.setup()
    global t_new, t_old, t_new_e, t_old_e, t_client_new, t_client_old, g_skip_shock
    g_skip_shock = not shared.services["shock_service_url"].startswith("http")
    t_new = AssemblyAPI(shared.services, shared.token, assembly_new)
    t_new_e = _Assembly(shared.services, shared.token, assembly_new)
    t_old = AssemblyAPI(shared.services, shared.token, assembly_old)
    t_old_e = _KBaseGenomes_ContigSet(shared.services, shared.token, assembly_old)
    t_client_new = AssemblyClientAPI(shared.services["assembly_service_url"], shared.token, assembly_new)
    t_client_old = AssemblyClientAPI(shared.services["assembly_service_url"], shared.token, assembly_old)


###### New Assembly Type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_assembly_id_new():
    _log.info("Input {}".format(assembly_new))
    assembly_id = t_new.get_assembly_id()
    _log.info("Output {}".format(assembly_id))
    assert isinstance(assembly_id, basestring) and len(assembly_id) > 0
    assembly_id_e = t_new_e.get_assembly_id()
    assert isinstance(assembly_id_e, basestring) and len(assembly_id_e) > 0
    assembly_id_c = t_client_new.get_assembly_id()
    assert isinstance(assembly_id_c, basestring) and len(assembly_id_c) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genome_annotations_new():
    _log.info("Input {}".format(assembly_new))
    annotations = t_new.get_genome_annotations()
    _log.info("Output {}".format(annotations))
    assert isinstance(annotations, list)
    annotations_e = t_new_e.get_genome_annotations()
    assert isinstance(annotations_e, list)
    assert annotations == annotations_e
    annotations_c = t_client_new.get_genome_annotations()
    assert isinstance(annotations_c, list)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_external_source_info_new():
    _log.info("Input {}".format(assembly_new))
    info = t_new.get_external_source_info()
    _log.info("Output {}".format(info))
    assert isinstance(info, dict)
    info_e = t_new_e.get_external_source_info()
    assert isinstance(info_e, dict) and info == info_e
    info_c = t_client_new.get_external_source_info()
    assert isinstance(info_c, dict) and info == info_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_stats_new():
    _log.info("Input {}".format(assembly_new))
    stats = t_new.get_stats()
    _log.info("Output {}".format(stats))
    assert isinstance(stats, dict)
    stats_e = t_new_e.get_stats()
    assert isinstance(stats_e, dict) and stats == stats_e
    stats_c = t_client_new.get_stats()
    assert isinstance(stats_c, dict) and stats == stats_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_number_contigs_new():
    _log.info("Input {}".format(assembly_new))
    count = t_new.get_number_contigs()
    _log.info("Output {}".format(count))
    assert isinstance(count, int) and count > 0
    count_e = t_new_e.get_number_contigs()
    assert isinstance(count_e, int) and count_e > 0 and count == count_e
    count_c = t_client_new.get_number_contigs()
    assert isinstance(count_c, int) and count_c > 0 and count == count_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gc_content_new():
    _log.info("Input {}".format(assembly_new))
    gc_content = t_new.get_gc_content()
    _log.info("Output {}".format(gc_content))
    assert isinstance(gc_content, float) and gc_content > 0.1
    gc_content_e = t_new_e.get_gc_content()
    assert isinstance(gc_content_e, float) and gc_content_e > 0.1
    gc_content_c = t_client_new.get_gc_content()
    assert isinstance(gc_content_c, float) and gc_content_c > 0.1


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_dna_size_new():
    _log.info("Input {}".format(assembly_new))
    dna_size = t_new.get_dna_size()
    _log.info("Output {}".format(dna_size))
    assert isinstance(dna_size, int) and dna_size > 0
    dna_size_e = t_new_e.get_dna_size()
    assert isinstance(dna_size_e, int) and dna_size > 0 and dna_size == dna_size_e
    dna_size_c = t_client_new.get_dna_size()
    assert isinstance(dna_size_c, int) and dna_size > 0 and dna_size == dna_size_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_lengths_new():
    _log.info("Input {}".format(assembly_new))
    contig_lengths = t_new.get_contig_lengths()
    _log.info("Output {}".format(len(contig_lengths)))
    assert isinstance(contig_lengths, dict) and len(contig_lengths) > 0
    contig_lengths_e = t_new_e.get_contig_lengths()
    assert isinstance(contig_lengths_e, dict) and len(contig_lengths_e) > 0
    contig_lengths_c = t_client_new.get_contig_lengths()
    assert isinstance(contig_lengths_c, dict) and len(contig_lengths_c) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_gc_content_new():
    _log.info("Input {}".format(assembly_new))
    contig_gc_content = t_new.get_contig_gc_content()
    _log.info("Output {}".format(len(contig_gc_content)))
    assert isinstance(contig_gc_content, dict) and len(contig_gc_content) > 0
    contig_gc_content_e = t_new_e.get_contig_gc_content()
    assert isinstance(contig_gc_content_e, dict) and len(contig_gc_content_e) > 0
    contig_gc_content_c = t_client_new.get_contig_gc_content()
    assert isinstance(contig_gc_content_c, dict) and len(contig_gc_content_c) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_ids_new():
    _log.info("Input {}".format(assembly_new))
    contig_ids = t_new.get_contig_ids()
    _log.info("Output {}".format(len(contig_ids)))
    assert isinstance(contig_ids, list) and len(contig_ids) > 0
    contig_ids_e = t_new_e.get_contig_ids()
    assert isinstance(contig_ids_e, list) and len(contig_ids_e) > 0
    contig_ids_c = t_client_new.get_contig_ids()
    assert isinstance(contig_ids_c, list) and len(contig_ids_c) > 0


@skipUnless(shared.can_connect and not g_skip_shock, 'Cannot connect to workspace')
def test_get_contigs_new():
    _log.info("Input {}".format(assembly_new))
    contigs = t_new.get_contigs()
    _log.info("Output {}".format(len(contigs)))
    assert isinstance(contigs, dict) and len(contigs) > 0
    contigs_e = t_new_e.get_contigs()
    assert isinstance(contigs_e, dict) and len(contigs_e) > 0
    contigs_c = t_client_new.get_contigs()
    assert isinstance(contigs_c, dict) and len(contigs_c) > 0


###### Old Assembly Type tests


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_assembly_id_old():
    _log.info("Input {}".format(assembly_old))
    assembly_id = t_old.get_assembly_id()
    _log.info("Output {}".format(assembly_id))
    assert isinstance(assembly_id, basestring) and len(assembly_id) > 0
    assembly_id_e = t_old_e.get_assembly_id()
    assert isinstance(assembly_id_e, basestring) and len(assembly_id_e) > 0 and assembly_id == assembly_id_e
    assembly_id_c = t_client_old.get_assembly_id()
    assert isinstance(assembly_id_c, basestring) and len(assembly_id_c) > 0 and assembly_id == assembly_id_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_genome_annotations_old():
    _log.info("Input {}".format(assembly_old))
    annotations = t_old.get_genome_annotations()
    _log.info("Output {}".format(annotations))
    assert isinstance(annotations, list)
    annotations_e = t_old_e.get_genome_annotations()
    assert isinstance(annotations_e, list)
    annotations_c = t_client_old.get_genome_annotations()
    assert isinstance(annotations_c, list)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_external_source_info_old():
    _log.info("Input {}".format(assembly_old))
    info = t_old.get_external_source_info()
    _log.info("Output {}".format(info))
    assert isinstance(info, dict)
    info_e = t_old_e.get_external_source_info()
    assert isinstance(info_e, dict)
    info_c = t_client_old.get_external_source_info()
    assert isinstance(info_c, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_stats_old():
    _log.info("Input {}".format(assembly_old))
    stats = t_old.get_stats()
    _log.info("Output {}".format(stats))
    assert isinstance(stats, dict)
    stats_e = t_old_e.get_stats()
    assert isinstance(stats_e, dict)
    stats_c = t_client_old.get_stats()
    assert isinstance(stats_c, dict)


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_number_contigs_old():
    _log.info("Input {}".format(assembly_old))
    count = t_old.get_number_contigs()
    _log.info("Output {}".format(count))
    assert isinstance(count, int) and count > 0
    count_e = t_old_e.get_number_contigs()
    assert isinstance(count_e, int) and count_e > 0 and count == count_e
    count_c = t_client_old.get_number_contigs()
    assert isinstance(count_c, int) and count_c > 0 and count == count_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_gc_content_old():
    _log.info("Input {}".format(assembly_old))
    gc_content = t_old.get_gc_content()
    _log.info("Output {}".format(gc_content))
    assert isinstance(gc_content, float) and gc_content > 0.1
    gc_content_e = t_old_e.get_gc_content()
    assert isinstance(gc_content_e, float) and gc_content_e > 0.1
    gc_content_c = t_client_old.get_gc_content()
    assert isinstance(gc_content_c, float) and gc_content_c > 0.1


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_dna_size_old():
    _log.info("Input {}".format(assembly_old))
    dna_size = t_old.get_dna_size()
    _log.info("Output {}".format(dna_size))
    assert isinstance(dna_size, int) and dna_size > 0
    dna_size_e = t_old_e.get_dna_size()
    assert isinstance(dna_size_e, int) and dna_size_e > 0 and dna_size == dna_size_e
    dna_size_c = t_client_old.get_dna_size()
    assert isinstance(dna_size_c, int) and dna_size_c > 0 and dna_size == dna_size_c


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_lengths_old():
    _log.info("Input {}".format(assembly_old))
    contig_lengths = t_old.get_contig_lengths()
    _log.info("Output {}".format(len(contig_lengths)))
    assert isinstance(contig_lengths, dict) and len(contig_lengths) > 0
    contig_lengths_e = t_old_e.get_contig_lengths()
    assert isinstance(contig_lengths_e, dict) and len(contig_lengths_e) > 0
    contig_lengths_c = t_client_old.get_contig_lengths()
    assert isinstance(contig_lengths_c, dict) and len(contig_lengths_c) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_gc_content_old():
    _log.info("Input {}".format(assembly_old))
    contig_gc_content = t_old.get_contig_gc_content()
    _log.info("Output {}".format(len(contig_gc_content)))
    assert isinstance(contig_gc_content, dict) and len(contig_gc_content) > 0
    contig_gc_content_e = t_old_e.get_contig_gc_content()
    assert isinstance(contig_gc_content_e, dict) and len(contig_gc_content_e) > 0
    contig_gc_content_c = t_client_old.get_contig_gc_content()
    assert isinstance(contig_gc_content_c, dict) and len(contig_gc_content_c) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contig_ids_old():
    _log.info("Input {}".format(assembly_old))
    contig_ids = t_old.get_contig_ids()
    _log.info("Output {}".format(len(contig_ids)))
    assert isinstance(contig_ids, list) and len(contig_ids) > 0
    contig_ids_e = t_old_e.get_contig_ids()
    assert isinstance(contig_ids_e, list) and len(contig_ids_e) > 0
    contig_ids_c = t_client_old.get_contig_ids()
    assert isinstance(contig_ids_c, list) and len(contig_ids_c) > 0


@skipUnless(shared.can_connect, 'Cannot connect to workspace')
def test_get_contigs_old():
    _log.info("Input {}".format(assembly_old))
    contigs = t_old.get_contigs()
    _log.info("Output {}".format(len(contigs)))
    assert isinstance(contigs, dict) and len(contigs) > 0
    contigs_e = t_old_e.get_contigs()
    assert isinstance(contigs_e, dict) and len(contigs_e) > 0
    contigs_c = t_client_old.get_contigs()
    assert isinstance(contigs_c, dict) and len(contigs_c) > 0