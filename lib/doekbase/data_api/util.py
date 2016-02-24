"""
Utility functions.

Includes:

- Logging initialization helper: get_logger()
- Logging decorators: @logged, @collect_performance
- Logging functions log_start(), log_end(), and log_event()

"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/4/15'

# stdlib
from collections import deque, namedtuple
from datetime import datetime
import logging
import logging.config
import os
import six
import threading
import time

# 3rd party
import psutil

# Message formats without/with timestamp
_KVSEP = '#'
_MESSAGE_FORMATS = [
    {'entry': '{func_name}.begin ' + _KVSEP + ' {kvp}',
     'exit' : '{func_name}.end ({dur}) ' + _KVSEP + ' {kvp}',
     'event': '{func_name} ' + _KVSEP + ' {kvp}'},
    {'entry': '{timestamp} {func_name}.begin ' + _KVSEP + ' {kvp}',
     'exit' : '{timestamp} {func_name}.end ({dur}) ' + _KVSEP + ' {kvp}',
     'event': '{timestamp} {func_name} ' + _KVSEP + ' {kvp}'},
]

# This flag controls whether the messages should include
# their own timestamp. External modules may set it.
include_timestamp = True

def default_message(mtype):
    return _MESSAGE_FORMATS[include_timestamp][mtype]

DEFAULT_LEVEL = logging.INFO
logformat = '%(levelname)s %(message)s'

g_running_nosetests = None

def get_logger(name=''):
    """Create and return a logger with the given name.
    The string 'doekbase.' is prepended to the name, if it is not
    already present.

    If we are running in nose, also prepend 'nose.' to the logger name
    so that `nose -v` options can apply to us. Nose checks are done only
    once, and cached.

    The created logger will propagate its messages to the parent.

    Args:
        name: Name of the new logger.

    Returns:
        same as `logging.getLogger()`
    """
    global g_running_nosetests
    # The doekbase namespace
    if not name.startswith('doekbase'):
        if name == '':
            name = 'doekbase'
        else:
            name = 'doekbase.' + name
    # Nose
    if g_running_nosetests is None:  # haven't checked yet
        g_running_nosetests = 'nose' in logging.root.manager.loggerDict
    if g_running_nosetests:
        name = 'nose.' + name
    # Create logger
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    logger.propagate = 1
    return logger

def basic_config(level=logging.INFO):
    log = get_logger()
    log.setLevel(level)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(logformat))
    log.addHandler(h)
    return log

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

# TODO turn example below into a test
def logged(logger, log_level=logging.INFO, log_name=None, **kw):
    """Wrap a method/function in a log start/end message.

    Example usage. Given the following code::

        @logged(g_log, log_name='hello')
        def hello_world(self, what):
            sys.stderr.write("hello {} world\n". format(what))

    Then the statement ``hello_world("dumb")`` should print output like::

        2015-08-26T01:02:30.123456 hello.begin
        hello dumb world
        2015-08-26T01:02:30.654321 hello.end
    
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
    fmt = fmt or default_message('entry')
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
    fmt = fmt or default_message('event')
    msg = fmt.format(**d)
    if level is None:
        level = DEFAULT_LEVEL
    logger.log(level, msg)
    return t0

def log_end(logger, t0, func_name, level=None, fmt=None, status_code=0,
            kvp=None):
    t1 = time.time()
    kvp_str = format_kvp(kvp, ',') if kvp else ''
    dur_str = '{:.6f}'.format(t1 - t0)
    d = dict(timestamp=format_timestamp(t1),
             func_name=func_name,
             kvp=kvp_str,
             dur=dur_str,
             status=status_code)
    fmt = fmt or default_message('exit')
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
            elif len(v) == 0:
                v = "''"
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
    MAX_SIZE = 1000  # max number events in history
    EVENT_WILDCARD = '*'

    def __init__(self, namespace='kbase'):
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
        if self._ns:
            full_event = '{}.{}'.format(self._ns, event)
        else:
            full_event = event
        pevent = PerfEvent(full_event, key, t0, timestamp, meta)
        for k in self._meta:
            pevent.add_metadata(k, self._meta[k])
        self._history.append(pevent)
        self._broadcast(event, 1, pevent)

    def get_last(self):
        if not self._history:
            return None
        return self._history[-1]

    def get_event(self, event, limit=0):
        """Get all performance events matching name `event`, up
        to `limit` number of entries (0=all).
        """
        # print('@@ events in history: {}'.format(
        #    [x.event for x in self._history]))
        if not self._history:
            result = []
        else:
            if event == self.EVENT_WILDCARD:
                limit = len(self._history) + 1
            n, result = 0, []
            for i in range(len(self._history) - 1, 0, -1):
                if self._history[i].event == event:
                    result.append(self._history[i])
                    n += 1
                    if n == limit:
                        break
        return result

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
                                     for k, v in item.metadata.items()])
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
        d.update({'event'    : self.event,
                  'key'      : self.key,
                  'timestamp': self.start_time,
                  'dur'      : self.duration})
        return d

def collect_performance(perf_collector, prefix='', suffix=''):
    """Decorator that simplifies the use of the `PerfCollector` class
    to collect and log performance for a single method.

    Example usage:
        pc = PerfCollector()
        @collect_performance(pc)
        def count_to_10():
            for i in range(1,11):
                print("i = {:d}".format(i))

    Args:
        perf_collector: Instance of PerfCollector class
        prefix: String prefix placed before the method name in order to
                make a log event name.
        suffix: String prefix placed after the method name in order to
                make a log event name.

    Returns:
        A method decorator
    """

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

def get_msgpack_object_ref(path):
    """Get object-id ref for object in messagepack-encoded file.

    Args:
        (str) path: Full path to file.
    Returns:
        (str) reference, in form A/B/C e.g. '93/111124/2'
    Raises:
        IOError if the file cannot be opened.
        ValueError if the data in the file cannot be decoded.
        KeyError if the reference field is not found in the data.
    """
    import msgpack
    try:
        f = open(path)
    except IOError as err:
        raise IOError('Cannot open file for reading: {}'.format(path))
    try:
        t = msgpack.load(f)
    except Exception as err:
        raise ValueError('Cannot decode messagepack data in path "{}": {}'
                         ''.format(path, err))
    try:
        ref = t['ref']
    except KeyError:
        raise KeyError('Field "ref" not found in object at "{}"'.format(path))
    return ref

class MonitorMemory(object):
    """Simple class to monitor memory in a separate thread, and
    trigger callbacks when available memory falls below a threshhold.

    Example usage::

       mm = MonitorMemory()
       def alert(avail, thresh, msg):
           print("ALERT! Available memory {:d} < {:d}. {}".format(
                 avail, thresh, msg))
       # call 'alert' when memory goes below 1GB
       mm.add_alert(1000, alert, "Be very afraid.")
       # run in a thread
       mm.run()
       # ...
       mm.stop()  # this blocks until the thread stops

    """
    check_interval_sec = 0.5

    def __init__(self):
        self._watchers = []
        self._thr = None
        self._stop_requested = False
        self._lock = threading.Lock()
        self.Watcher = namedtuple('Watcher', ['bytes', 'cb', 'args'])

    def add_alert(self, thresh_mb, callback, *args):
        """Add a new alert to be called back when the available
        memory falls below a threshhold (in MBytes).

        Args:
            thresh_mb (int): Threshhold in MBytes, e.g. 1024 = 1GB
            callback: Function to call when memory falls below the
                      threshhold. Function should have signature
                      ``f(mon, avail, thresh, *args)``, where:
                          * 'mon' is the instance of this class
                          * 'avail' is bytes currently available,
                          * 'thresh' is the threshhold in bytes,
                          * and remaining args are from 'args'.
            *args: Remaining arguments to provide to callback.

        Returns:
            self (for chaining)
        """
        thresh_bytes = thresh_mb * 1024 * 1024
        watcher = self.Watcher(bytes=thresh_bytes, cb=callback, args=list(args))
        with self._lock:
            self._watchers.append(watcher)

    def start(self):
        """Start a thread to monitor the memory.
        If the thread is already running, this does nothing.
        """
        if self._thr is not None:
            return
        self._thr = threading.Thread(target=self._run, args=())
        self._thr.daemon = True
        self._thr.start()

    def stop(self):
        """Stop the thread as soon as possible.
        This blocks until the thread exits.
        If the thread is not running, this does nothing.
        """
        if self._thr is None:
            return
        self._stop_requested = True

    def join(self):
        """Wait for the thread to finish.
        """
        self._thr.join()
        self._thr = None

    def _run(self):
        """Run"""
        while not self._stop_requested:
            time.sleep(self.check_interval_sec)
            vmem = psutil.virtual_memory()
            alerts_triggered = []
            with self._lock:
                n, i = len(self._watchers), 0
                while i < n:
                    w = self._watchers.pop()
                    if vmem.available < w.bytes:
                        alerts_triggered.append((w.cb,
                                                 [self, vmem.available,
                                                  w.bytes] + w.args))
                        # remove this watcher now that it has fired
                    else:
                        # keep this watcher (insert at other end)
                        self._watchers.insert(0, w)
                    i += 1
            # invoke, highest threshhold first (reverse-sort by bytes)
            alerts_triggered.sort(cmp=lambda a, b: cmp(a[1][2], b[1][2]),
                                  reverse=True)
            for cb, args in alerts_triggered:
                cb(*args)
        # print('@@ stopped')
        return
