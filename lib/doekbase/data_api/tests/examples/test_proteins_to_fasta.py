
"""
Advanced data API examples.
"""

__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '11/06/15'


from doekbase.data_api.tests import shared
from doekbase.data_api.tests.examples.proteins_to_fasta import *


def setup():
    shared.setup()

def test_examples():
    url = shared.services['workspace_service_url']
    proteins_to_fasta.run(url)

