"""
Verify that all examples in ``assembly_api`` are runnable.

When you add a new example, add a call to it, here.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '10/14/15'

import os
from doekbase.data_api.tests import shared
from doekbase.data_api.tests.examples.assembly_cross_annotation import run
#from doekbase.data_api.sequence.assembly.api import AssemblyAPI
#import doekbase.data_api.tests.examples.test_get_core_exons_for_gene
#import doekbase.data_api.tests.examples.test_get_mRNAs_for_genes_to_GFF

temp_files = []

def setup():
    shared.setup()

def test_examples():
    global temp_files
    url = shared.services['workspace_service_url']
    data=run(url)
    #temp_files.append()
    #temp_files.append(test_get_core_exons_for_gene.run(url))
    #temp_files.append(test_get_mRNAs_for_genes_to_GFF.run(url))

def cleanup():
    map(os.unlink, temp_files)

