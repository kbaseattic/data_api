# Stdlib

# Third-party
import twisted.internet
import twisted.web

from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol

# Local
from doekbase.data_api.taxonomy.taxon.service import thrift_service
from doekbase.data_api.taxonomy.taxon.service.interface import TaxonService
from doekbase.data_api.util import get_logger

DEFAULT_WS_URL = 'https://ci.kbase.us/services/ws/'
DEFAULT_SHOCK_URL = 'https://ci.kbase.us/services/shock-api/'

_log = get_logger('thrift')  # set up a logger for Thrift messages

def get_services_dict(ws=DEFAULT_WS_URL, shock=DEFAULT_SHOCK_URL):
    return {'workspace_service_url': ws,
            'shock_service_url': shock}

#TODO respond to kill signals
#TODO on HUP reload of config
def start_service(services = None, host = 'localhost', port = 9101):
    if services is None:
        services = get_services_dict()

    handler = TaxonService(services)
    processor = thrift_service.Processor(handler)
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    resource = TTwisted.ThriftResource(processor, pfactory, pfactory)
    site = twisted.web.server.Site(resource = resource)
    server = twisted.internet.reactor.listenTCP(port, site, interface=host)

    _log.info('Starting the server...')
    twisted.internet.reactor.run()
    _log.info('Server stopped.')
    return 0
