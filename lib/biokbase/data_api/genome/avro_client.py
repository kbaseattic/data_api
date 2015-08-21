"""
Description.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/20/15'

# Imports

# Stdlib
import json
import logging
# Third-party
import avro.ipc as ipc
import avro.protocol as protocol
# Local
from biokbase.data_api import avro_rpc
from biokbase.data_api.util import get_logger
from biokbase.data_api.util import log_start, log_end, log_event
from biokbase.data_api.genome import api
from biokbase.data_api.genome import avro_spec

# Logging

_log = get_logger('genome.api.avro_client')

# Classes and functions

PROTOCOL = protocol.parse(avro_spec.proto)

class GenomeAnnotationAvro(api.GenomeAnnotationClient):
    def __init__(self, host='localhost', port=avro_rpc.AVRO_DEFAULT_PORT):
        super(GenomeAnnotationAvro, self).__init__()
        t0 = log_start(_log, 'avro_connect')
        client = ipc.HTTPTransceiver(host, port)
        self._requestor = ipc.Requestor(PROTOCOL, client)
        log_end(_log, t0, 'avro_connect')

    def get_info(self, ref):
        params = {'ref': {'objid': ref}}
        t0 = log_start(_log, 'get_info')
        r = self._requestor.request('get_info', params)
        r['info'] = json.loads(r['info'])
        log_end(_log, t0, 'get_info')
        return r

    def get_taxon(self, ref):
        params = {'objid': ref}
        r = self._requestor.request('get_taxon', params)
        return r

api.genome_annotation_clients.register(api.CLIENT_TYPE_AVRO, GenomeAnnotationAvro)