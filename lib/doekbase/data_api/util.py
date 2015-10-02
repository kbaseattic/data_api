"""
Utility functions.

Includes:
    - Logging decorators
    - Logging functions log_start() and log_end()
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/4/15'

from collections import deque
from datetime import datetime
import logging
import logging.config
import os
import six
import time

ENTRY_MESSAGE = '{timestamp} {func_name}.begin {kvp}'
EXIT_MESSAGE = '{timestamp} {func_name}.end {dur} {kvp}'
EVENT_MESSAGE = '{timestamp} {func_name} {kvp}'

DEFAULT_LEVEL = logging.INFO
DEFAULT_LEVEL_NAME = logging.getLevelName(DEFAULT_LEVEL)
DEFAULT_CONFIG = {
    'version': 1,
    'formatters': {
        'basic': { 'format': '%(levelname)s %(message)s' }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
            'stream': 'ext://sys.stderr',
            'level': DEFAULT_LEVEL_NAME
        }
    },
    'root': {
        'handlers': ['console'],
        'level': DEFAULT_LEVEL_NAME
    }
}

_configuration = None

def get_logger(name, config=DEFAULT_CONFIG):
    """Called by other modules to get a logger,
    and set or change the configuration.
    """
    global _configuration

    # Perform configuration/reconfiguration if necessary.
    # Usually none of this is done.
    if _configuration is None:
        assert config is not None  # need something!
        logging.config.dictConfig(config)
        _configuration = config  # first time
    elif config is DEFAULT_CONFIG and _configuration is DEFAULT_CONFIG:
        pass  # quickly check the common case
    elif config != _configuration:
        assert config is not None
        logging.config.dictConfig(config)  # reconfigure
        _configuration = config

    # Get the logger, given the current configuration.
    return logging.getLogger(name)


class Timer(object):
    def __init__(self):
        self._timings = []
        self._start = time.time()

    def __enter__(self):
        self._start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        t = time.time()
        dt, self._start = t - self._start, t
        self._timings.append(dt)

    def pop(self):
        return self._timings.pop()

def logged(logger, log_level=logging.INFO, log_name=None, **kw):
    """Wrap a method/function in a log start/end message.
    """
    def real_decorator(method, logger_name=logger.name):
        # choose name for logged event
        func_name = log_name or method.__name__
        full_name = logger_name + '.' + func_name
        # format any key/value pairs
        kvp_str = format_kvp(kw, ',') if kw else ''

        # create wrapper
        def method_wrapper(self, *args, **kwds):
            t0 = log_start(logger, full_name, level=log_level, kvp=kvp_str)
            returnval = method(self, *args, **kwds)
            log_end(logger, t0, full_name, level=log_level, kvp=kvp_str)
            return returnval
        # return wrapper
        return method_wrapper

    return real_decorator

def log_start(logger, func_name, level=None, fmt=None, kvp=None):
    t0 = time.time()
    kvp_str = format_kvp(kvp, ',') if kvp else ''
    d = dict(timestamp=format_timestamp(t0),
             func_name=func_name, kvp=kvp_str)
    fmt = fmt or ENTRY_MESSAGE
    msg = fmt.format(**d)
    if level is None:
        level = DEFAULT_LEVEL
    logger.log(level, msg)
    return t0

def log_event(logger, func_name, level=None, fmt=None, kvp=None):
    t0 = time.time()
    kvp_str = format_kvp(kvp, ',') if kvp else ''
    d = dict(timestamp=format_timestamp(t0),
             func_name=func_name, kvp=kvp_str)
    fmt = fmt or EVENT_MESSAGE
    msg = fmt.format(**d)
    if level is None:
        level = DEFAULT_LEVEL
    logger.log(level, msg)
    return t0

def log_end(logger, t0, func_name, level=None, fmt=None, status_code=0, kvp=None):
    t1 = time.time()
    kvp_str = format_kvp(kvp, ',') if kvp else ''
    d = dict(timestamp=format_timestamp(t1),
             func_name=func_name,
             kvp=kvp_str,
             dur=(t1 - t0),
             status=status_code)
    fmt = fmt or EXIT_MESSAGE
    if level is None:
        level = DEFAULT_LEVEL
    logger.log(level, fmt.format(**d))

def format_kvp(d, sep):
    """Format key-value pairs as a string."""
    pairs = []
    for k, v in d.items():
        if isinstance(v, six.string_types):
            if sep in v:
                v = v.replace(',', '\\,')
        pairs.append((k, v))
    s = sep.join(['{}={}'.format(k, v) for k, v in pairs])
    return s

# Format a timestamp as an ISO8601 string.
format_timestamp = lambda t: datetime.fromtimestamp(t).isoformat()

def get_auth_token():
    try:
        return os.environ["KB_AUTH_TOKEN"]
    except KeyError:
        raise Exception(
            "Missing authentication token! "
            "Set KB_AUTH_TOKEN environment variable.")

# Simple performance classes

class PerfCollector(object):
    """Collector of multiple performance events.
    """
    MAX_SIZE = 1000 # max number events in history

    def __init__(self, namespace):
        self._ns = namespace
        self._history = deque(maxlen=self.MAX_SIZE)
        self._cur = {}
        self._make_key = lambda e, k: '{e}::{k}'.format(e=e, k=k)

    def start_event(self, event, key):
        timestamp = time.time()
        ekey = self._make_key(event, key)
        self._cur[ekey] = timestamp

    def end_event(self, event, key, **meta):
        timestamp = time.time()
        ekey = self._make_key(event, key)
        if not ekey in self._cur:
            raise KeyError('No current event found for key "{}"'
                           .format(ekey))
        t0 = self._cur[ekey]
        del self._cur[ekey]
        full_event = '{}.{}'.format(self._ns, event)
        pevent = PerfEvent(full_event, key, t0, timestamp, meta)
        self._history.append(pevent)

    def get_last(self):
        return self._history[-1]

class PerfEvent(object):
    """Single timed event.

    Events can be extracted using dictionary syntax,
    e.g. my_event['<key'], with the keys:
    """
    def __init__(self, event, key, start_time, end_time, meta):
        """Ctor.

        Args:
          event (str): Full name of event <namespace>.<event-name>
          key (str): Identifying key
          start_time (float): Unix epoch seconds for start
          end_time (float): Floating point time in seconds for end
          meta (dict) : Additional key/value pairs
        """
        self.event = event
        self.key = key
        self.start = start_time
        self.end = end_time
        self.duration = end_time - start_time
        self._meta = meta

    def __getitem__(self, key):
        if key in ('event', 'key', 'start', 'end', 'duration'):
            return getattr(self, key)
        if key in self._meta:
            return self._meta[key]
        raise KeyError(key)
