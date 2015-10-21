"""
Shared by test code
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/11/15'

# Stdlib
import logging
import os

# Local
from doekbase.data_api.core import ObjectAPI, g_ws_url, g_shock_url
from doekbase.data_api.util import get_logger
from doekbase.data_api import cache

genome = "PrototypeReferenceGenomes/kb|g.166819"

try:
    token = os.environ["KB_AUTH_TOKEN"]
except KeyError:
    token = None

# Logging
_log = None
services = None

# Globals

g_redis_host = os.environ.get('KB_REDIS_HOST', None)
if g_redis_host == "":
    g_redis_host = None
g_redis_port = int(os.environ.get('KB_REDIS_PORT', '6379'))
g_redis_bin = os.environ.get('KB_REDIS_SERVER', '/usr/local/bin/redis-server')
g_redis_conf = os.environ.get('KB_REDIS_CONF', 'redis.conf')

# Functions and classes
def get_services():
    svc = {"workspace_service_url": g_ws_url,
            "shock_service_url": g_shock_url}
    #print("@@ service URLs = {}".format(svc))
    return svc

def can_connect(ref=genome):
    """See if we can get a connection to the workspace and access the
    given reference.

    Args:
      ref (str): Workspace object reference
    Returns:
      (bool) if it can be accessed
    """
    try:
        _ = ObjectAPI(services=get_services(), ref=ref)
    except Exception as err:
        _log.exception(err)
        _log.warn('Connect and fetch object failed: {}'.format(err))
        return False
    return True

def determine_can_connect(workspaces):
    """Replace value with connection status.
       Now we can simply refer to the dict entry in future tests. Also add
       a special 'all' to handle all features in a given workspace.

    Args:
      workspaces (dict): 2-level dict of {'name': {'name2': 'full-ws-id', .. }}
    """
    for num in workspaces:
        all_objects = True
        for ref in workspaces[num]:
            if isinstance(workspaces[num][ref], bool):
                continue # skip, already determined
            ok = can_connect(workspaces[num][ref])
            workspaces[num][ref] = ok
            all_objects = all_objects and ref
        workspaces[num]['all'] = all_objects
    return workspaces

# Print this when we skip a function due to inability to fetch
# required objects
connect_fail = 'Cannot fetch all required objects from workspace'

def setup():
    global _log, services
    _log = get_logger('doekbase.data_api.tests.shared')
    services = get_services()
    if g_redis_host is not None:
        cache.ObjectCache.cache_class = cache.RedisCache
        cache.ObjectCache.cache_params = {
            'redis_host': g_redis_host,
            'redis_port': g_redis_port}

def teardown():
    pass
