"""
RPC-related utility functions
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/24/15'

# Imports

# Stdlib
import argparse
import enum
import math
import re
import sys
# Third-party
from thrift.Thrift import TType

# Constants

FIXME = '// FIXME'

# Classes and functions

class InvalidField(Exception):
    def __init__(self, dtype, name, value):
        s = 'Value "{}" of field {} is not of type "{}"'
        msg = s.format(value, name, dtype.name)
        Exception.__init__(self, msg)

class ThriftTypes(enum.Enum):
    # can validate these
    BOOL = TType.BOOL
    DOUBLE = TType.DOUBLE
    I16 = TType.I16
    I64 = TType.I64
    MAP = TType.MAP
    VOID = TType.VOID
    I32 = TType.I32
    I08 = TType.I08
    BYTE = TType.BYTE
    STRING = TType.STRING
    UTF16 = TType.UTF16
    UTF8 = TType.UTF8
    UTF7 = TType.UTF7
    LIST = TType.LIST
    SET = TType.SET
    # not sure how to validate these
    STOP = TType.STOP
    STRUCT = TType.STRUCT

class ThriftInputValue(object):
    def __init__(self, dtype, value):
        if value is None:
            self.valid = True # XXX: warning?
            self.empty = True
            return
        self.empty = False
        self.valid = True  # if not known, it's valid
        if dtype.value == TType.STRING:
            self.valid = isinstance(value, (str, unicode))
        elif dtype.value == TType.BOOL:
            self.valid = isinstance(value, bool)
        elif dtype.value == TType.DOUBLE:
            self.valid = isinstance(value, (int, float))
        elif dtype.value in (TType.I08, TType.I16,  TType.I32, TType.I64, TType.BYTE):
            # Allow floats with no fractional part to get converted.
            # Floats with non-zero fractional parts will fail.
            if isinstance(value, float) and math.floor(value) == value:
                value = int(value)
            self.valid = isinstance(value, int)
        elif dtype.value in (TType.STRING, TType.UTF16, TType.UTF8,
                       TType.UTF7):
            self.valid = isinstance(value, (str, unicode))
        elif dtype.value in (TType.LIST, TType.SET):
            self.valid = isinstance(value, (tuple, list, set))
        elif dtype.value == TType.MAP:
            self.valid = isinstance(value, TType.MAP)

def thrift_validate(obj):
    """Validate an auto-generated datatype from the Thrift `ttypes` module.

    Automatically extract the fields to be validated from the `thrift_spec`
    attribute in the `obj`.

    Validation has the following features:
      - unicode or non-unicode strings are equivalent
      - an integer value is valid for a floating-point field
      - a floating-point value is valid for a floating-point field, if and
        only if the value has no fractional part (i.e. floor(value) == value)

    Args:
      obj: Object to validate.

    Return: The input object (for chaining)
    """
    assert hasattr(obj, 'thrift_spec')
    for item in getattr(obj, 'thrift_spec'):
        if item is None:
            continue # skip it
        dtype, name = ThriftTypes(item[1]), item[2]
        value = getattr(obj, name)
        iv = ThriftInputValue(dtype, value)
        if not iv.valid:
            raise InvalidField(dtype, name, value)
    return obj

class KIDLToThriftConverter(object):
    """Convert KIDL to Thrift IDL
    """

    CONTAINER_MAPPING = {'mapping': 'map',
                         'list': 'list',
                         'tuple': 'list'}

    def __init__(self, lines):
        self._ln = lines

    def process(self):
        i = 0
        result = []
        while i < len(self._ln):
            s = self._ln[i]
            if re.match('\s*typedef\s+structure\s*\{', s):
                r, offs = self.change_struct(self._ln, i)
                i += offs
                result.extend(r)
            elif re.match('\s*typedef\s+', s):
                o = s[:s.rfind(';')]
                if '<' in o:
                    o += FIXME
                result.append(o)
                i += 1
            else:
                result.append(s)
                i += 1
        return result

    def change_struct(self, ln, p):
        result = ['struct {} {{']
        i, done, fieldnum = 0, False, 1
        while not done:
            s = ln[p + i]
            if re.match('\s*\}', s):
                o = '}'
                m = re.match('\s*\}\s*(\w+)', s)
                name = m.group(1)
                result[0] = result[0].format(name)
                done = True
            elif re.match('.*;\s*', s):
                num = '{:d}: '.format(fieldnum)
                if re.match('\s*(mapping|list|tuple)\s*<', s):
                    s = self.change_container(s)
                o = num + s[:s.rfind(';')]
                fieldnum += 1
            else:
                o = s
            result.append(o)
            i += 1
        return result, i

    def change_container(self, s):
        if re.search('<.*?<', s):
            return s + FIXME + ';'
        m = re.match('\s*(\w+)\s*<', s)
        ctype = m.group(1)
        m = re.match('\s*{}\s*<\s*((\w+).*?)(,'
                     '\s*(\w+).*?)*>'.format(ctype), s)
        new_ctype = self.CONTAINER_MAPPING[ctype]
        groups = m.groups()
        if groups[-1] is None:  # only 1 match
            groups = groups[:2]
        result = '  ' + new_ctype + '<{}>;'.format(', '.join(groups[1::2]))
        return result

def kidl_to_thrift_main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', metavar='path', help='Input filename')
    ap.add_argument('--ofile', help='Output filename', dest='ofile',
                    default=None, metavar='path')
    args = ap.parse_args()

    fname = args.file
    try:
        lines = open(fname).read().split('\n')
    except IOError as err:
        print('Error opening input file: {}'.format(err))
        return -1
    ostream = sys.stdout

    if args.ofile is not None:
        try:
            ostream = open(args.ofile, 'w')
        except IOError as err:
            print('Error opening output file: {}'.format(err))
            return -2
    converter = KIDLToThriftConverter(lines)
    outlines = converter.process()
    ostream.write('\n'.join(outlines))

    return 0

if __name__ == '__main__':
    sys.exit(kidl_to_thrift_main())