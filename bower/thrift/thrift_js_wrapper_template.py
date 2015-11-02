"""
Create Thrift JS wrapper template.

The output will not be a working program, but it should
reduce most of the tedium of creating the wrapper for each method.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '10/30/15'

import argparse
import itertools
import logging
import os
import sys

from doekbase.data_api.util import get_logger
from doekbase.data_api.thriftutil import extract_thrift_descriptions

_log = get_logger(__name__)

method_template = """
        /**
         * {description}
         *
         * @returns .
         */
        function {name} {{
            return Promise.resolve(client().{name}(authToken, objectReference,
                                   true));
        }}
"""

summary_template = """
{ind}// API
{ind}return Object.freeze({{
{mapping}
{ind}}});
"""

def print_template(data, strm):
    for key, val in data.items():
        method = method_template.format(name=key, description=val)
        strm.write(method)
    indent = ' ' * 8
    mapping_str = ',\n'.join(['{}    {}: {}'.format(indent, k, k) for k in data])
    strm.write(summary_template.format(ind=indent, mapping=mapping_str))

def parse_main_docstring():
    """Parse the main docstring into two parts by breaking on the first
    line with only whitespace (or nothing at all except the newline).
    """
    s = __doc__.split('\n')
    while not s[0].strip():
        s = s[1:]
    desc = list(itertools.takewhile(lambda x: x.strip(), s))
    rest = s[len(desc) + 1:]
    return ' '.join(desc), ' '.join(rest)

def main(cmdline):
    desc, desc2 = parse_main_docstring()
    cwd = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description=desc, epilog=desc2)
    parser.add_argument('source', help='Source .thrift file')
    parser.add_argument('--out', help='Output file (default=stdout)',
                        dest='outfile')
    parser.add_argument('--verbose', '-v', dest='vb', action="count", default=0,
                        help="Print more verbose messages to standard error. "
                             "Repeatable. (default=ERROR)")
    args = parser.parse_args(cmdline)

    verbosity = (logging.ERROR, logging.WARNING, logging.INFO,
                 logging.DEBUG)[min(args.vb, 3)]
    _log.setLevel(verbosity)
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter('%(isotime)s [%(levelname)s] %(message)s'))
    _log.addHandler(_h)

    try:
        if args.outfile:
            outfile = open(args.outfile, 'w')
        else:
            outfile = sys.stdout
    except Exception as err:
        parser.error('Opening output file: {}'.format(err))

    desc = extract_thrift_descriptions(args.source)
    print_template(desc, outfile)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))