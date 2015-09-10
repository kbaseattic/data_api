"""
Shared by test code
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/11/15'

import logging
import os

from doekbase.data_api.core import ObjectAPI

_log = None
FORMAT = "%(funcName)s() %(message)s"

services = {
    "workspace_service_url": "https://ci.kbase.us/services/ws/",
    "shock_service_url": "https://ci.kbase.us/services/shock-api/",
}
genome = 'PrototypeReferenceGenomes/kb|g.3157'

token = os.environ["KB_AUTH_TOKEN"]

def can_connect():
    try:
        _ = ObjectAPI(services=services, token=token, ref=genome)
        return True
    except Exception, e:
        _log.exception(e)
        _log.warn('Cannot connect to workspace! Most tests will be skipped')
        return False

def setup():
    logging.basicConfig(format=FORMAT)
    _log = logging.getLogger()
