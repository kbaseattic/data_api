"""
Example scripts for the Taxon API.

"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/18/15'

# Stdlib
import os
# Third-party
# Local
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI

def fetch_and_print_taxon():
    # Initialize API with target object
    taxon = TaxonAPI(token=os.environ.get('KB_AUTH_TOKEN'), ref='1019/4')
    # Now the methods of the instance can be used to fetch and show
    # taxonomic information
    print('Got taxon "{} ({})"'.format(taxon.get_scientific_name(),
                                        taxon.get_taxonomic_id()))
