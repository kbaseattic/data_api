"""
Base classes and utility functions for Data API service classes.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '12/24/15'

# Imports
# -------

# Stdlib
import time
import traceback

# Third party
import twisted.internet
import twisted.web
from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTwisted

# Local
from doekbase.data_api import exceptions, core

# Global constants and variables
# ------------------------------

DEFAULT_WS_URL = 'https://ci.kbase.us/services/ws/'
DEFAULT_SHOCK_URL = 'https://ci.kbase.us/services/shock-api/'

SERVICES_DICT = {'workspace_service_url': DEFAULT_WS_URL,
                 'shock_service_url': DEFAULT_SHOCK_URL}

# Functions and classes
# ---------------------

def server_method(func):
    """Decorator for service methods.

    The wrapper depends on the existence of two attributes in the
    class being wrapped:
        
    1. ttypes (module): Thrift type module, containing exception classes
    2. log (logging.Logger): Logger instance

    Args:
        func (function): Function being wrapped
    """
    def wrapper(self, token, ref, *args, **kwargs):
        assert hasattr(self, 'log'), 'Method in wrapped class must have "log" ' \
                                     'attribute'
        assert hasattr(self, 'ttypes'), 'Method in wrapped class must have ' \
                                      '"ttypes" attribute'
        error, result = None, None
        self.log.debug('method={meth} state=begin token={tok} ref={ref} args={'
                       'args} kwargs={kw}'
                   .format(meth=func.__name__, tok=token, ref=ref,
                           args=args, kw=kwargs))
        t0 = time.time()
        try:
            result = func(self, token, ref, *args, **kwargs)
        except AttributeError, e:
            error = e
            raise self.ttypes.AttributeException(e.message,
                                                 traceback.format_exc())
        except exceptions.AuthenticationError, e:
            error = e
            raise self.ttypes.AuthenticationException(e.message,
                                                      traceback.format_exc())
        except exceptions.AuthorizationError, e:
            error = e
            raise self.ttypes.AuthorizationException(e.message,
                                                     traceback.format_exc())
        except exceptions.TypeError, e:
            error = e
            raise self.ttypes.TypeException(e.message, traceback.format_exc())
        except Exception, e:
            error = e
            raise self.ttypes.ServiceException(e.message, traceback.format_exc(),
                                               {"ref": str(ref)})
        finally:
            if error is None:
                self.log.debug('method={meth} state=end token={tok} ref={ref} '
                               'args={args} kwargs={kw} dur={t:.3f}'
                           .format(meth=func.__name__, tok=token, ref=ref,
                                   args=args, kw=kwargs,
                                   t=time.time() - t0))
            else:
                self.log.error('method={meth} state=error token={tok} '
                          'ref={ref} args={args} kwargs={kw}'
                           'error_message="{m}" dur={t:.3f}'
                          .format(meth=func.__name__, tok=token, ref=ref,
                                  args=args, kw=kwargs, m=error.message,
                                  t=time.time() - t0))
        return result

    return wrapper

class BaseService(object):
    """Base class for Data API service classes, which will be defined
    in the 'interface' module of the appropriate API subdirectory.

    Takes care of some boilerplate logging and error-checking, as well
    as setting up instance variables for the @server_method decorator.
    """
    def __init__(self, log, ttypes_module, api_class, services=None):
        """Constructor.

        Args:
            log (logging.Logger): For logging service activity
            ttypes_module: Thrift ttypes module for the API
            api_class: the API library class, e.g.,
                       `doekbase.data_api.taxonomy.taxon.api.TaxonAPI`
            services (dict): Service configuration dictionary, passed to
                             constructor of the `api_class`.
        """
        self.log = log
        self.ttypes = ttypes_module
        self._api_class = api_class
        self.log.debug('method=__init__ state=begin services={s}'
                       .format(s=services))
        try:
            if services is None or not isinstance(services, dict):
                raise TypeError("You must provide a service configuration " +
                                "dictionary! Found {0}".format(type(services)))
            elif not services.has_key("workspace_service_url"):
                raise KeyError("Expecting workspace_service_url key!")
        except Exception as e:
            self.log.error('method=__init__ state=error services={s}'
                           'error_message="{m}"'
                           .format(s=services, m=e.message))
            raise
        self.services = services
        self.log.debug('method=__init__ state=end services={s} '
                       .format(s=services))

    def _get_instance(self, *args):
        """Return an instance of the API. Use this level of indirection to
        allow future optimizations over creating it each time.
        """
        return self._api_class(self.services, *args)

class BaseClientConnection(object):
    """Base class for <ServiceName>ClientConnection objects defined
    in the data_api.<api.path>.service.interface module.
    """
    def __init__(self, thrift_client, url):
        if not hasattr(thrift_client, 'Client') or not callable(
                thrift_client.Client):
            raise AttributeError('Invalid "thrift_client" argument')
        self.client = None
        self.transport = None
        self.protocol = None

        try:
            self.transport = THttpClient.THttpClient(url)
            self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
            self.client = thrift_client.Client(self.protocol)
        except AssertionError as err:
            raise ValueError('Invalid Thrift client URL: "{}"'.format(url))
        except TTransport.TTransportException as err:
            raise RuntimeError(
                'Cannot connect to remote Thrift service at {}: {}'
                .format(url, err.message))

    def get_client(self):
        return self.transport, self.client

# For service drivers

# TODO respond to kill signals
# TODO on HUP reload of config
def start_service(api_class, service_class, log,
                  services=None, host='localhost', port=9100):
    """Start a Data API service.

    Args:
        api_class (BaseService): The custom API service class, e.g.,
                    `doekbase.data_api.taxonomy.taxon.api.TaxonService`
        service_class (type): The Thrift auto-generated service class
        log (logging.Logger): Logging object
        services (dict): Service configuration dictionary, passed to
                         constructor of the `api_class`.
        host (str): Service host (will default to 'localhost')
        port (int): Service port, e.g. 9101
    """
    assert issubclass(api_class, BaseService), \
        'Invalid "api_class": must be a subclass of ' \
        'doekbase.data_api.service_core.BaseService'
    assert hasattr(service_class, 'Processor'), 'Invalid "service_class": ' \
                                                'missing "Processor" attribute'
    assert isinstance(port, int), 'The "port" must be an integer'
    log.debug('method=start_service state=begin host={host} port={port:d}'
               .format(host=host, port=port))

    # Create server
    services = services or SERVICES_DICT
    handler = api_class(services)
    processor = service_class.Processor(handler)
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    resource = TTwisted.ThriftResource(processor, pfactory, pfactory)
    site = twisted.web.server.Site(resource=resource)
    twisted.internet.reactor.listenTCP(port, site, interface=host)

    # Run server
    sname = api_class.__name__
    shost = host or 'localhost'
    log.info('msg="Starting {} server at {}:{}"'.format(sname, shost, port))
    log.debug('method=twisted.internet.reactor.run state=begin')
    try:
        twisted.internet.reactor.run()
    except Exception as err:
        log.error('msg="Abort {} server on error"'.format(sname))
        log.error('method=twisted.internet.reactor.run state=error '
                   'error_message={e}'.format(e=err))
        raise
    finally:
        log.debug('method=twisted.internet.reactor.run state=end')
    return 0

def stop_service():
    twisted.internet.reactor.stop()