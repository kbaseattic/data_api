"""
Service implementation.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/14/15'

import logging
import time

import spec_pb2 as pb
import impl
from biokbase.data_api import workspace_db, util

_version = pb.SemVer(version='1.0.0b', major=1, minor=0, other='0b')

_log = logging.getLogger(__name__)
util.stdout_config(_log)

_ONE_DAY_IN_SECONDS = 60*60*24

class GenomeAnnotationServicer(pb.EarlyAdopterGenomeAnnotationAPIServicer):
    def __init__(self):
        # connect to the workspace (XXX: re-use this)
        conn = workspace_db.connect()
        # initialize the API
        self._api = impl.GenomeAnnotationAPI(conn)

    @util.logmethod(_log)
    def get(self, request, context):
        """Get one genome annotation."""
        obj = self._api.get(request.ref)
        response = pb.GenomeAnnotation(version=_version, ident=obj.objid)
        return response

    @util.logmethod(_log)
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
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop()

if __name__ == '__main__':
    main()
