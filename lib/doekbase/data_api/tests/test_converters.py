"""
Battery of tests for code in the converters sub-package.

This also serves as documentation for usage of the modules.
See in particular functions called `test_<type>_convert`.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '5/26/16'

# Stdlib
import logging
from unittest import SkipTest, TestCase
# Local
from . import shared
from doekbase.data_api.converters import genome
from doekbase.data_api.converters.base import GenomeName

# Target workspace in CI environment
TEST_CI_WS_NAME = "Converter-Test-Narrative"
TEST_CI_WS_ID = '7609'

g_kbase_instance = 'ci'

################################################################
# Connection test
################################################################

g_can_connect = None

def setup():
    global g_can_connect
    level = logging.INFO
    genome.set_converter_loglevel(level)
    shared.setup()
    if g_can_connect is None:
        shared._log.info('Trying to connect to "{}" workspace for objects: {}, {}'.format(
            g_kbase_instance, TEST_CI_ASM_OBJID, TEST_CI_GA_OBJID))
        try:
            g_can_connect = shared.can_connect(ref=TEST_CI_ASM_OBJID, deployment_config=g_kbase_instance) and \
                         shared.can_connect(ref=TEST_CI_GA_OBJID, deployment_config=g_kbase_instance)
        except:
            pass
        if not g_can_connect:
            shared._log.warn('Cannot connect to "{}" workspace'.format(g_kbase_instance))

def skip_unless_connect():
    if not g_can_connect:
        raise SkipTest('Could not connect to "{}" workspace'.format(g_kbase_instance))

################################################################
# GenomeAnnotation -> Genome / ContigSet
################################################################

# Input GenomeAnnotation reference object in CI
TEST_CI_GA_OBJID = '6052/40/1'

def test_genome_annotation_init():
    """Init GA converter, but don't run convert"""
    skip_unless_connect()
    _ga_init()

def _ga_init():
    return genome.GenomeConverter(ref=TEST_CI_GA_OBJID, kbase_instance=g_kbase_instance)

def test_genome_annotation_convert():
    """Init and run GA converter on a test object"""
    skip_unless_connect()
    obj = _ga_init()
    result = obj.convert(TEST_CI_WS_ID)
    assert(result)

################################################################
# Assembly -> ContigSet
################################################################

TEST_CI_ASM_OBJID = '6052/31/1'

def test_assembly_init():
    """Init Assembly converter, but don't run convert"""
    skip_unless_connect()
    _asm_init()

def _asm_init():
    return genome.AssemblyConverter(ref=TEST_CI_ASM_OBJID, kbase_instance=g_kbase_instance)

def test_assembly_convert():
    """Init and run Assembly converter on a test object"""
    skip_unless_connect()
    obj = _asm_init()
    result = obj.convert(TEST_CI_WS_ID)
    assert(result)

################################################################
# Utility functions
################################################################

class GenomeNameTests(TestCase):
    def test_demo(self):
        base = '1234'
        source = 'refseq'
        print('With base={} and source={}:'.format(base, source))
        gn = GenomeName(base, source)
        print('GenomeAnnotation: {}'.format(gn.get_genome_annotation()))
        print('Assembly: {}'.format(gn.get_assembly()))
        print('Genome: {}'.format(gn.get_genome()))
        print('ContigSet: {}'.format(gn.get_contigset()))

    def test_genome_name_nosource_new(self):
        base = 'foobar'
        gn = GenomeName(base)
        assert base in gn.get_assembly()
        assert GenomeName.legacy not in gn.get_assembly()
        assert base in gn.get_genome_annotation()
        assert GenomeName.legacy not in gn.get_genome_annotation()
        if GenomeName.annotation_type:
            assert GenomeName.annotation_type in gn.get_genome_annotation()
        else:
            assert not gn.get_genome_annotation().endswith('_genomeannotation')
            assert not gn.get_genome_annotation().endswith('_annotation')

    def test_genome_name_source_new(self):
        base, src = 'foobar', 'yomama'
        gn = GenomeName(base, source=src)
        assert base in gn.get_assembly()
        assert src in gn.get_assembly()
        assert GenomeName.legacy not in gn.get_assembly()
        assert base in gn.get_genome_annotation()
        assert src in gn.get_genome_annotation()
        assert GenomeName.legacy not in gn.get_genome_annotation()

    def test_genome_name_nosource_old(self):
        base = 'foobar'
        gn = GenomeName(base)
        assert base in gn.get_contigset()
        assert GenomeName.legacy in gn.get_contigset()
        assert base in gn.get_genome()
        assert GenomeName.legacy in gn.get_genome()

    def test_genome_name_source_old(self):
        base, src = 'foobar', 'yomama'
        gn = GenomeName(base, source=src)
        assert base in gn.get_contigset()
        assert src in gn.get_contigset()
        assert GenomeName.legacy in gn.get_contigset()
        assert base in gn.get_genome()
        assert src in gn.get_genome()
        assert GenomeName.legacy in gn.get_genome()
