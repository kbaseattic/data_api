"""
Service implementation.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/14/15'

# Imports

# Stdlib
import argparse
import json
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

VERSION = dict(version='1.0.0b', major=1, minor=0, suffix='0b')
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
        self._api = impl.GenomeAnnotationImpl(self._conn)
        self._cache = Cache()

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

    def get_info(self, req):
        objid = req['ref']['objid']
        method = 'info'
        t0 = log_start(_log, 'get.genome_annotation', kvp={'objid':objid})
        result = self._cache.get((method, objid), None)
        if result is None:
            print("@@ getting new object")
            obj = self._api.get_info(objid)
            info = obj.info
            info_str = json.dumps(info)
            result = {'version': VERSION, 'ident': str(obj.objid),
                      'info': info_str}
            self._cache.add(result, objid, method)
        else:
            print("@@ using cached object")
        log_end(_log, t0, 'get.genome_annotation', kvp={'result': result})
        return result

    def get_taxon(self, req):
        objid = req['ref']['objid']
        t0 = log_start(_log, 'get.taxon')
        obj = self._api.get(objid)
        tx_obj = self._api.get_taxon(obj)
        result = {'version': VERSION, 'ident': str(obj.objid)}
        log_end(_log, t0, 'get.taxon')
        return result

class Cache(object):
    """Simple in-memory cache.

    Uses object identity combined with methods that have been invoked
    on the object to determine whether the data is already available.
    """
    def __init__(self):
        # key = object identifier
        # value = ([set,of,method,names], datum)
        self._data = {}

    def get(self, key, default=None):
        try:
            value = self[key]
        except KeyError:
            value = default
        return value

    def __getitem__(self, method_and_id):
        if not len(method_and_id) == 2:
            raise ValueError('expected tuple ("method_name", <id>)')
        method, id_ = method_and_id
        try:
            item = self._data[id_]
        except KeyError:
            raise KeyError('identifier {id} not found'.format(id=id_))
        if not self._has_methods(item, {method}):
            raise KeyError('method {m} not invoked on data'.format(m=method))
        return item[1]

    @staticmethod
    def _has_methods(item, methods):
        return methods.issubset(item[0])

    def add(self, datum, ident, method):
        item = self._data.get(ident, None)
        methods = {method}
        if item and self._has_methods(item, methods):
            return False
        elif item is None:
            self._data[ident] = [methods, datum]
        else:
            self._data[ident][0] = self._data[ident][0].union(methods)
        return True

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', dest='host', default='localhost',
                    metavar='ADDR', help='Listening host interface. '
                                         'Use 0.0.0.0 for "all". '
                                         '(default=%(default)s)')
    ap.add_argument('--port', dest='port', default=avro_rpc.AVRO_DEFAULT_PORT,
                    metavar='PORT', help='Listening port '
                                         '(default=%(default)d)')
    args = ap.parse_args()
    kw = {'host': args.host, 'port': args.port}
    avro_rpc.run_service(GenomeAnnotationService, **kw)
