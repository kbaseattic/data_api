"""
RPC-related utility functions
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/24/15'

# Imports

# Stdlib
import argparse
import enum
import re
import sys
# Third-party
from thrift.Thrift import TType

# Constants

FIXME = '// FIXME'

# Classes and functions

# class ThriftTypes(enum.Enum):
# TType.BOOL
# TType.DOUBLE
# TType.I16
# TType.I64
# TType.MAP
# TType.STOP
# TType.STRUCT
# TType.UTF7
# TType.VOID
# TType.BYTE
# TType.I08
# TType.I32
# TType.LIST
# TType.SET
# TType.STRING
# TType.UTF16
# TType.UTF8

class InvalidField(object):
    def __init__(self, dtype, name, value):
        s = 'Value "{}" of field {} is not of type "{}"'
        self._msg = s.format(value, name, dtype)

    def __str__(self):
        return self._msg

def thrift_validate(obj):
    invalid_fields = []
    assert hasattr(obj, 'thrift_spec')
    for item in getattr(obj, 'thrift_spec'):
        if item is None:
            continue # skip it
        dtype, name = item[1], item[2]
        value = getattr(obj, name)
        if value is None:
            # XXX: warning?
            continue
        if dtype == TType.STRING:
            if not(isinstance(value, str) or
                       isinstance(value, unicode)):
                invalid_fields.append(InvalidField(dtype, name, value))

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