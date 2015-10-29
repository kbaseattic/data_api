
"""
Verify that all examples in ``taxon_api`` are runnable.

When you add a new example, add a call to it, here.
"""

__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/19/15'

from doekbase.data_api.tests.examples.taxon_api import *
from doekbase.data_api.tests import shared

def setup():
    shared.setup()

def test_examples():
    url = shared.services['workspace_service_url']
    fetch_and_print_taxon(url)