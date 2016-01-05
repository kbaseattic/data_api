"""
Service driver for Taxon API.
"""

# Imports
# -------
# Local
from doekbase.data_api import service_core
from doekbase.data_api.taxonomy.taxon.service import thrift_service
from doekbase.data_api.taxonomy.taxon.service.interface import TaxonService
from doekbase.data_api.util import get_logger

_log = get_logger(__name__)

def start_service(services=None, host='localhost', port=9101):
    return service_core.start_service(TaxonService, thrift_service, _log,
                                      services=services, host=host, port=port)
