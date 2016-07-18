"""
Unit tests for FASTA download
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '4/15/16'

from unittest import skipUnless

from . import shared
from doekbase.data_api.sequence.assembly import api
try:
    import cStringIO as StringIO
except:
    import StringIO
import unittest

assembly_new = "ReferenceGenomeAnnotations/kb|g.166819_assembly/1"
assembly_old = "OriginalReferenceGenomes/kb|g.166819.contigset/1"

def setup():
    shared.setup()

def test_create_fasta_old():
    assembly = api.AssemblyAPI(services=shared.services, token=shared.token, ref=assembly_old)
    output = StringIO.StringIO()
    assembly.get_fasta().to_file(output)
    basic_fasta_validation(output.getvalue())

# def test_create_fasta_new():
#     assembly = api.AssemblyAPI(services=shared.services, token=shared.token, ref=assembly_new)
#     output = StringIO.StringIO()
#     assembly.get_fasta().to_file(output)
#     basic_fasta_validation(output.getvalue())

def basic_fasta_validation(s):
    newline1 = s.find('\n')
    line1 = s[:newline1]
    newline2 = s.find('\n', newline1 + 1)
    line2 = s[newline1 + 1:newline2]
    assert line1.startswith('>')
    assert line2[0] in 'agctuAGCTU'

