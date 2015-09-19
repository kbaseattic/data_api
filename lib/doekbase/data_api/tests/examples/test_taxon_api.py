"""
Verify that all examples in ``taxon_api`` are runnable.

When you add a new example, add a call to it, here.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/19/15'

from .taxon_api import *

def test_examples():
    fetch_and_print_taxon()