"""
Utility functions and classes for running Thrift services/clients.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>, Erik Pearson'
__date__ = '10/28/15'

# Stdlib
import logging
import re
# Local
from doekbase.data_api.util import get_logger

_log = get_logger('thriftutil')  # set up a logger for Thrift messages
_log.setLevel(logging.DEBUG)

def str_prefix(s, num):
    prefix = s[:num]
    if len(s) > num:
        prefix += '...'
    return prefix

DESCRIPTION_RE = re.compile('''
\s*/\*\*(.*?)        # Comment start
(?:\.\\n|\\n\\n).*?  # end of description
\*/\s*\\n            # Comment end
\s*[a-zA-Z0-9_<>,]+\s+(\w+)\s*\(.*   # Method declaration
''', flags=re.X | re.M | re.S)

def extract_thrift_descriptions(src):
    """Extract descriptions from Thrift file.

    Recognizes comments of the form:

        /**
         * This is the description, ended by a period
         * or a blank line.
         * This is not part of the description.
         *

    Args:
      src (str): Name of source code file
    Returns:
      dict<str,str>: Mapping of method names to descriptive text
    """
    descriptions = {}
    with open(src, 'r') as f:
        chunk = ''
        for line in f:
            s = line.strip()
            if chunk and (s.startswith('/**') or not s):
                _log.debug('Thrift method:<<{}>>'.format(chunk))
                match = DESCRIPTION_RE.match(chunk)
                if match:
                    d1 = match.group(1).strip()
                    d2 = d1.split('\n')
                    d3 = ' '.join([d4[d4.find('*') + 1:].strip()
                                   for d4 in d2])
                    desc = d3.strip()
                    name = match.group(2)
                    descriptions[name] = desc
                else:
                    # Print a warning if this looks like it
                    # is a function.
                    if '(' in chunk and ')' in chunk and 'throws' in chunk:
                        _log.warn('Not recognized as a documented method: {}'
                                  .format(str_prefix(chunk, 20)))
                chunk = line.strip()
                _log.debug('Reset text block to: {}'.format(chunk))
            else:
                chunk += line

    _log.debug('Descriptions found for: {}'.format(descriptions.keys()))

    return descriptions

# def main():
#     server = taxon_service()  # XXX: Run alternate ones
#     print('Starting the server...')
#     server.serve()
#     print('done.')
#     return 0
#
# if __name__ == '__main__':
#     sys.exit(main())
