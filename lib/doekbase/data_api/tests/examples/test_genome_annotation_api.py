"""
Verify that all examples in ``taxon_api`` are runnable.

When you add a new example, add a call to it, here.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '10/14/15'

from doekbase.data_api.tests.examples.genome_annotation_api import *
from doekbase.data_api.tests import shared

# Some known reference genomes
genome_new = "PrototypeReferenceGenomes/kb|g.166819"
genome_old = "OriginalReferenceGenomes/kb|g.166819"

def setup():
    shared.setup()

def test_examples():
    url = shared.services['workspace_service_url']
    get_proteins_for_gene(genome_new, 'some gene', ws_url=url)