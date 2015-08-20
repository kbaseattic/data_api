"""
Service implementation.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/14/15'

import time

import spec_pb2 as pb
import impl
from biokbase.data_api import workspace_db
from biokbase.data_api.util import get_logger, logged, log_start, log_end

_version = pb.SemVer(version='1.0.0b', major=1, minor=0, other='0b')

_log = get_logger('genome.svc')

_ONE_DAY_IN_SECONDS = 60*60*24

class GenomeAnnotationServicer(pb.EarlyAdopterGenomeAnnotationAPIServicer):
    def __init__(self):
        # connect to the workspace (XXX: re-use this)
        conn = workspace_db.connect()
        # initialize the API
        self._api = impl.GenomeAnnotationAPI(conn)

    @logged(_log)
    def get(self, request, context):
        """Get one genome annotation."""
        obj = self._api.get(request.ref)
        response = pb.GenomeAnnotation(version=_version, ident=str(obj.objid))
        print("sending response: {}".format(response))
        return response

    @logged(_log)
    def get_taxon(self, request, context):
        """Get a taxon in an annotation."""
        ga_obj = self._api.get(request.ref)
        tx_obj = self._api.get_taxon(ga_obj)  # TODO: use this
        response = pb.Taxon(version=_version, ident=ga_obj.objid,
                            lineage_parts=[], taxid='e. coli', aliases=[])
        return response

def main():
    server = pb.early_adopter_create_GenomeAnnotationAPI_server(
        GenomeAnnotationServicer(), 50051, None, None)
    server.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        server.stop()

if __name__ == '__main__':
    main()
