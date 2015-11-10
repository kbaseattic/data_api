"""
Verify that all examples in ``taxon_api`` are runnable.

When you add a new example, add a call to it, here.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '10/14/15'

import os
from genome_annotation_api import *
from doekbase.data_api.tests import shared

temp_files = []

def setup():
    shared.setup()

def test_examples():
    global temp_files
    url = shared.services['workspace_service_url']
    temp_files.append(proteins_to_fasta(url))

def cleanup():
    map(os.unlink, temp_files)

