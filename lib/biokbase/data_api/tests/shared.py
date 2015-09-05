"""
Shared by test code
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/11/15'

# Imports

# Local
from biokbase.data_api.core import ObjectAPI, g_ws_url, g_shock_url
from biokbase.data_api.util import get_logger

# Logging

_log = get_logger('data_api.tests.shared')

# Globals

genome = 'PrototypeReferenceGenomes/kb|g.3157'

# Functions and classes

def get_services():
    return {"workspace_service_url": g_ws_url,
            "shock_service_url": g_shock_url}

def can_connect():
    try:
        _ = ObjectAPI(services=get_services(), ref=genome)
    except Exception, e:
        _log.exception(e)
        _log.warn('Cannot connect to workspace! Most tests will be skipped')
        return False
    return True

def setup():
    pass

def teardown():
    pass