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
logformat = '%(levelname)s %(message)s'

g_running_nosetests = None

def get_logger(name):
    global g_running_nosetests
    if not name.startswith('doekbase.'):
        name = 'doekbase.' + name
    # If we are running in nose, nest under there so nose -v options
    # can apply to us. Cache the result of checking for nose in a global var.
    if g_running_nosetests is None:  # haven't checked yet
         g_running_nosetests = 'nose' in logging.root.manager.loggerDict
    if g_running_nosetests:
         name = 'nose.' + name
    # create logger
    logger = logging.getLogger(name)
#    logger.propagate = 1
    return logger

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
    EVENT_WILDCARD = '*'

    def __init__(self, namespace):
        self._ns = namespace
        self._history = deque(maxlen=self.MAX_SIZE)
        self._cur = {}
        self._make_key = lambda e, k: '{e}::{k}'.format(e=e, k=k)
        self._observers = {}
        self._meta = {}

    def add_observer(self, event, start_fn, end_fn):
        """Add observer functions for an event.

        Args:
          event (str): Event name or EVENT_WILDCARD for all events.
          start_fn: Function taking (event, key, timestamp) or None
          end_fn: Function taking (event, PerfEvent) or None
        """
        if event in self._observers:
            self._observers[event].append((start_fn, end_fn))
        else:
            self._observers[event] = [(start_fn, end_fn)]

    def _broadcast(self, event, idx, *args):
        if event in self._observers:
            for obs in self._observers[event]:
                if obs[idx]:
                    obs[idx](event, *args)
        if self.EVENT_WILDCARD in self._observers:
            for obs in self._observers[self.EVENT_WILDCARD]:
                if obs[idx]:
                    obs[idx](event, *args)

    def set_metadata(self, meta):
        self._meta = meta

    def start_event(self, event, key):
        timestamp = time.time()
        ekey = self._make_key(event, key)
        self._cur[ekey] = timestamp
        self._broadcast(event, 0, key, timestamp)

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
        for k in self._meta:
            pevent.add_metadata(k, self._meta[k])
        self._history.append(pevent)
        self._broadcast(event, 1, pevent)

    def get_last(self):
        if not self._history:
            return None
        return self._history[-1]

    def dump(self, stream):
        by_event = {}
        for item in self._history:
            if item.event in by_event:
                by_event[item.event].append(item)
            else:
                by_event[item.event] = [item]
        stream.write("Event                          Duration  Metadata\n")
        for event in sorted(by_event.keys()):
            for item in by_event[event]:
                meta_str = ' '.join(['{k}={v}'.format(k=k, v=v)
                                     for k,v in item.metadata.items()])
                stream.write("{e:30s} {d:8.3f}  {m}\n".format(
                    e=event[:30], d=item.duration, m=meta_str))

class PerfEvent(object):
    """Single timed event.

    Events can be extracted using dictionary syntax,
    e.g. my_event['<key'], for any key in the metadata.
    This will also work for any of the attributes, in case it's
    more convenient to get at them that way.

    Attributes:
        event (str): Full name of event <namespace>.<event-name>
        key (str): Identifying key
        start(float): Start timestamp, in seconds since 1/1/1970
        end (float): End timestamp, in seconds since 1/1/1970
        duration (float): Duration in seconds
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

    def add_metadata(self, key, value):
        """Modify the metadata by setting `value` for `key`.
        """
        self._meta[key] = value

    @property
    def metadata(self):
        """Return a *copy* of the metadata.
        """
        return self._meta.copy()

    def __getitem__(self, key):
        if key in ('event', 'key', 'start', 'end', 'duration'):
            return getattr(self, key)
        if key in self._meta:
            return self._meta[key]
        raise KeyError(key)

    def as_dict(self):
        d = self._meta.copy()
        d.update({'event': self.event,
                'key': self.key,
                'timestamp': self.start_time,
                'dur': self.duration})
        return d

def collect_performance(perf_collector, prefix='', suffix=''):
    def real_decorator(method):
        event = prefix + method.__name__ + suffix
        key = str(time.time())
        # create wrapper
        def method_wrapper(self, *args, **kwds):
            perf_collector.start_event(event, key)
            returnval = method(self, *args, **kwds)
            for i, a in enumerate(args):
                kwds['_{:d}'.format(i)] = str(a)
            perf_collector.end_event(event, key, **kwds)
            return returnval

        # return wrapper
        return method_wrapper

    return real_decorator
