"""
Battery of tests for code in the converters sub-package.

This also serves as documentation for usage of the modules.
See in particular functions called `test_<type>_convert`.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '5/26/16'

import logging
from . import shared
from doekbase.data_api.converters import genome

def setup():
    level = logging.INFO
    genome.set_converter_loglevel(level)
    shared.setup()

# Target workspace in CI environment
TEST_CI_WS_NAME = "Converter-Test-Narrative"
TEST_CI_WS_ID = '7609'

################################################################
# GenomeAnnotation -> Genome / ContigSet
################################################################

# Input GenomeAnnotation reference object in CI
TEST_CI_GA_OBJID = '6052/40/1'

def test_genome_annotation_init():
    """Init converter, but don't run convert"""
    _ga_init()

def _ga_init():
    return genome.GenomeConverter(ref=TEST_CI_GA_OBJID, kbase_instance='ci')

def test_genome_annotation_convert():
    """Init and run converter on a test object"""
    obj = _ga_init()
    result = obj.convert(TEST_CI_WS_ID)
    assert(result)

################################################################
# Assembly -> ContigSet
################################################################

TEST_CI_ASM_OBJID = '6052/31/1'

def test_assembly_init():
    """Init converter, but don't run convert"""
    _asm_init()

def _asm_init():
    return genome.AssemblyConverter(ref=TEST_CI_ASM_OBJID, kbase_instance='ci')

def test_assembly_convert():
    """Init and run converter on a test object"""
    obj = _asm_init()
    result = obj.convert(TEST_CI_WS_ID)
    assert(result)
