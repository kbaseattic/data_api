"""
Service implementation.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/14/15'

# Imports

# Stdlib
import re
# Third-party
import avro.ipc as ipc
import avro.protocol as protocol
import avro.schema as schema
# Local
import impl
from biokbase.data_api import workspace_db
from biokbase.data_api.util import get_logger
from biokbase.data_api.util import log_start, log_end, log_event
from biokbase.data_api.genome import avro_spec
from biokbase.data_api import avro_rpc

# Logging

_log = get_logger('genome.api.server')

# Constants

VERSION = dict(version='1.0.0b', major=1, minor=0, other='0b')
PROTOCOL = protocol.parse(avro_spec.proto)
VALID_METHOD = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*')

# Exceptions

class ServerError(schema.AvroException): pass

class InvalidMethodName(ServerError):
    def __init__(self, name):
        msg = 'Internal error: method name {} does not match pattern {}'\
            .format(name, VALID_METHOD.pattern)
        super(InvalidMethodName, self).__init__(msg)

class UnknownMethod(ServerError): pass

# Classes and functions

class GenomeAnnotationService(ipc.Responder):
    def __init__(self):
        ipc.Responder.__init__(self, PROTOCOL)
        self._conn = workspace_db.connect()
        self._api = impl.GenomeAnnotationAPI(self._conn)

    def invoke(self, msg, req):
        t0 = log_start(_log, 'genome.service.invoke')
        method = msg.name
        if not VALID_METHOD.match(method) or method == 'invoke':
            raise InvalidMethodName(method)
        if not hasattr(self, method):
            raise UnknownMethod(method)
        t1 = log_start(_log, 'genome.service.method.{}'.format(method))
        result = getattr(self, method)(req)
        log_end(_log, t1, 'genome.service.method.{}'.format(method))
        log_end(_log, t0, 'genome.service.invoke')
        return result

    def get(self, req):
        objid = req['ref']['objid']
        t0 = log_start(_log, 'get.genome_annotation', kvp={'objid':objid})
        obj = self._api.get(objid)
        result = {'ver': VERSION, 'ident': str(obj.objid)}
        log_end(_log, t0, 'get.genome_annotation')
        return result

    def get_taxon(self, req):
        objid = req['ref']['objid']
        t0 = log_start(_log, 'get.taxon')
        obj = self._api.get(objid)
        tx_obj = self._api.get_taxon(obj)
        result = {'ver': VERSION, 'ident': str(obj.objid)}
        log_end(_log, t0, 'get.taxon')
        return result


if __name__ == '__main__':
    avro_rpc.run_service(GenomeAnnotationService)
