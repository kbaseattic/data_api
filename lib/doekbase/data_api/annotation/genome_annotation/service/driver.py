"""
Service driver for GenomeAnnotation API.
"""

# Imports
# -------
# Local
from doekbase.data_api import service_core
from doekbase.data_api.annotation.genome_annotation.service import thrift_service
from doekbase.data_api.annotation.genome_annotation.service.interface import GenomeAnnotationService
from doekbase.data_api.util import get_logger

_log = get_logger(__name__)

def start_service(services=None, host='localhost', port=9103):
    return service_core.start_service(GenomeAnnotationService, thrift_service, _log,
                                      services=services, host=host, port=port)
