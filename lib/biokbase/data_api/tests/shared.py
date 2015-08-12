"""
Shared by test code
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/11/15'

import logging

from biokbase.data_api.assembly import AssemblyAPI

can_connect = False
services = {
    "workspace_service_url": "https://ci.kbase.us/services/ws/",
    "shock_service_url": "https://ci.kbase.us/services/shock-api/",
}
genome = 'PrototypeReferenceGenomes/kb|g.3157'

def setup():
    global can_connect

    logging.basicConfig()
    _log = logging.getLogger()

    try:
        _ = AssemblyAPI(services=services, ref=genome + '_assembly')
        can_connect = True
    except:
        _log.warn('Cannot connect to workspace! Most tests will be skipped')
