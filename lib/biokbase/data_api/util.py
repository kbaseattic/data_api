"""
Utility functions.

Includes:
    - Logging decorators
    - Logging functions log_start() and log_end()
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/4/15'

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
        'basic': { 'format': '%(message)s' }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
            'stream': 'ext://sys.stdout'
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

## Examples

_example_logger = None

def run_examples():
    @logged(_example_logger)
    def func_one(*args):
        print("I am logged")

    @logged(_example_logger, name='joe')
    def func_two(*args):
        print("I am also logged")

    func_one()
    func_two()

if __name__ == '__main__':
    global _example_logger
    _example_logger = get_logger('example')
    print("In Main")
    run_examples()

def get_auth_token():
    try:
        return os.environ["KB_AUTH_TOKEN"]
    except KeyError:
        raise Exception(
            "Missing authentication token! "
            "Set KB_AUTH_TOKEN environment variable.")

