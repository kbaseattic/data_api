"""
Description.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/20/15'

# Imports

# Stdlib
# Third-party
import avro.ipc as ipc
import avro.protocol as protocol
# Local
from biokbase.data_api.util import get_logger
from biokbase.data_api.util import log_start, log_end
from biokbase.data_api.genome import api
from biokbase.data_api.genome import avro_spec

# Logging

_log = get_logger('genome.api.avro_client')

# Classes and functions

PROTOCOL = protocol.parse(avro_spec.proto)

rq_params = lambda x: {'message': x}

class GenomeAnnotationAvro(api.GenomeAnnotationClient):
    def __init__(self, host='localhost', port=9090):
        super(GenomeAnnotationAvro, self).__init__()
        log_start(_log, 'avro_connect')
        client = ipc.HTTPTransceiver(host, port)
        self._requestor = ipc.Requestor(PROTOCOL, client)
        log_end(_log, 'avro_connect')

    def get(self, ref):
        params = rq_params({'objid': ref})
        r = self._requestor.request('get', params)
        return r

    def get_taxon(self, ref):
        params = rq_params({'objid': ref})
        r = self._requestor.request('get_taxon', params)
        return r