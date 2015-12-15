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

def fetch_and_print_taxon(ws_url='https://ci.kbase.us/services/ws/'):
    """Fetch Taxon from Workspace Service.

    Args:
      ws_url (str): a service address or a local directory
         containing a downloaded version of the data created with the
         ``dump_wsfile`` utility.
    """
    # Initialize API with target object
    taxon_ref = 'ReferenceTaxons/242159_taxon'
    # Try to connect to remote service
    taxon = TaxonAPI(token=os.environ.get('KB_AUTH_TOKEN'), ref=taxon_ref,
                     services={'workspace_service_url': ws_url})
    # Now the methods of the instance can be used to fetch and show
    # taxonomic information
    print('Got taxon "{} ({})"'.format(taxon.get_scientific_name(),
                                        taxon.get_taxonomic_id()))

