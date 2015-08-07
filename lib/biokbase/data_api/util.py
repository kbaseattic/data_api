"""
Utility functions.

Includes:
    - Logging decorators
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/4/15'

from datetime import datetime
import functools
import logging
import six
import sys
import time

# Create a default logger to stdout
default_logger = logging.getLogger('default')
_hdlr = logging.StreamHandler(stream=sys.stdout)
_hdlr.setFormatter(logging.Formatter("%(message)s"))
default_logger.addHandler(_hdlr)

class logged(object):
    """Logging decorator.

    The format of the output for function entry and exit
    is controlled by the class variables, `ENTRY_MESSAGE` and
    `EXIT_MESSAGE`. These are pre-processed by `.format()`
    with a dictionary including per-function key/value
    pairs and some provided values:
        - timestamp: ISO8601 UTC timestamp, to microseconds
        - func_name: Name of function
        - dur: Duration between the ENTRY and EXIT
               as a floating point #seconds
        - kvp: User-provided key/value pairs, formatted as
          "key=value" separated by commas

    Usage:

       @logged
       def func_one(args):
          print("I am logged")

        @logged(name='joe')
        def func_two(args):
          print("I am also logged")

        # Output:

        2015-08-04T11:08:10.046121 func_one.begin/
        I am logged
        2015-08-04T11:08:10.046320 func_one.end 0.00019907951355/
        2015-08-04T11:08:10.046465 func_two.begin/name=joe
        I am also logged
        2015-08-04T11:08:10.046575 func_two.end 0.000110149383545/name=joe

    """
    ENTRY_MESSAGE = '{timestamp} {func_name}.begin/{kvp}'
    EXIT_MESSAGE = '{timestamp} {func_name}.end {dur}/{kvp}'

    def __init__(self, logger=None, **kvp):
        self.logger = default_logger if logger is None else logger
        if kvp:
            self.kvp_str = format_kvp(kvp, ',')
        else:
            self.kvp_str = ''
        self.level = logging.INFO

    def __call__(self, func):
        """Returns a wrapper that wraps func.
        The wrapper will log the entry and exit points of the function
         with logging.INFO level.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            t0 = time.time()
            d = dict(timestamp=format_timestamp(t0),
                     func_name=func.__name__,
                     kvp=self.kvp_str)
            msg = self.ENTRY_MESSAGE.format(**d)
            self.logger.log(self.level, msg)
            f_result = func(*args, **kwds)
            t1 = time.time()
            d['timestamp'] = format_timestamp(t1)
            d['dur'] = t1 - t0
            self.logger.log(self.level, self.EXIT_MESSAGE.format(**d))
            return f_result
        return wrapper

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

@logged()
def func_one(*args):
    print("I am logged")

@logged(name='joe')
def func_two(*args):
    print("I am also logged")


if __name__ == '__main__':
    print("In Main")
    default_logger.setLevel(logging.INFO)
    func_one()
    func_two()
