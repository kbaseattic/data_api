# Stdlib

# Third-party
import twisted.internet
import twisted.web

from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol

# Local
from doekbase.data_api.annotation.genome_annotation.service import thrift_service
from doekbase.data_api.annotation.genome_annotation.service.interface import GenomeAnnotationService
from doekbase.data_api.util import get_logger

DEFAULT_WS_URL = 'https://ci.kbase.us/services/ws/'
DEFAULT_SHOCK_URL = 'https://ci.kbase.us/services/shock-api/'

# set up a logger for Thrift messages
_log = get_logger('.'.join([__name__, 'service']))

def get_services_dict(ws=DEFAULT_WS_URL, shock=DEFAULT_SHOCK_URL):
    return {'workspace_service_url': ws,
            'shock_service_url': shock}

#TODO respond to kill signals
#TODO on HUP reload of config
def start_service(services = None, host = 'localhost', port = 9103):
    _log.debug('method=start_service state=begin host={h} port={p:d}'
              .format(h=host, p=port))
    if services is None:
        services = get_services_dict()

    handler = GenomeAnnotationService(services)
    processor = thrift_service.Processor(handler)
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    resource = TTwisted.ThriftResource(processor, pfactory, pfactory)
    site = twisted.web.server.Site(resource = resource)
    server = twisted.internet.reactor.listenTCP(port, site, interface=host)

    _log.info('Starting the server')
    _log.debug('method=twisted.internet.reactor.run state=begin')
    try:
        twisted.internet.reactor.run()
    except Exception as err:
        _log.error('Abort on error')
        _log.error('method=twisted.internet.reactor.run state=error '
                   'error_message={e}'.format(e=err))
        raise
    finally:
        _log.debug('method=twisted.internet.reactor.run state=end')
    return 0
