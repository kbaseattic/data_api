
"""
Verify that all examples in ``taxon_api`` are runnable.

When you add a new example, add a call to it, here.
"""

__author__ = 'Dan Gunter <mjoachimiak@lbl.gov>'
__date__ = '11/06/15'

from doekbase.data_api.tests.examples.taxon_api import *
from doekbase.data_api.tests import shared
import doekbase.data_api.tests.examples.proteins_to_fasta
import proteins_to_fasta


def setup():
    shared.setup()

def test_examples():
    url = shared.services['workspace_service_url']
    proteins_to_fasta.run()

