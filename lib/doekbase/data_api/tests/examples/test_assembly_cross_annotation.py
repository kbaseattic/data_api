
__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '01/07/16'

import os
from genome_annotation_api import *
from doekbase.data_api.tests import shared
from doekbase.data_api.tests.examples.proteins_to_fasta import run
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

