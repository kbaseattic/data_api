#!/usr/bin/env python
"""
Insert method descriptions from a .thrift file in another source
code file.

Currently supported source code files:
  Python
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '10/20/15'

import argparse
import logging
import os
import re
import sys

# Logging

_log = logging.getLogger('kbase.insert_thrift_docs')
_h = logging.StreamHandler()
_h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
_log.addHandler(_h)

# Globals

SOURCE_EXT = {'py'}
THRIFT_FUNC_RE = re.compile('\S+\s+([a-z_]+)\(')

# Classes and functions

def str_prefix(s, num):
    prefix = s[:num]
    if len(s) > num:
        prefix += '...'
    return prefix

PYTHON_FUNC_RE = re.compile(
    '\s*@abc.abstractmethod\s*\\n'
    '\s*def\s+(\w+)\s*\(.*?\):\s*\\n'
    '\s*"""(.*?)(?:\.\\n|\\n\\n).*?',
    flags=re.X | re.M | re.S)

def extract_python_methods(src):
    """Extract method bodies from Python file.

    Args:
      src (str): Name of source code file
    Returns:
      dict<str,str>: Mapping of method names to descriptive text
    """
    methods = {}

    with open(src, 'r') as f:
        chunk, in_docstring = '', False
        for line in f:
            # See whether we are in/out of docstring by looking for
            # triple-quotes. Do nothing if there are 2 pairs of
            # triple-quotes on the same line.
            p1 = line.find('"""')
            if p1 >= 0:
                p2 = line.find('"""', p1 + 1)
                if p2 < 0:
                    in_docstring = not in_docstring
            # At a blank line, not inside a docstring, process current chunk
            if line.strip() == '' and not in_docstring:
                name, method = None, None
                _log.debug("Python method: {}".format(chunk))
                match = PYTHON_FUNC_RE.match(chunk)
                if match:
                    # function name is first inner group
                    name = match.group(1)
                    # replace description, in second group, with a placeholder
                    desc_start, desc_end = match.span(2)
                    chunk = chunk[:desc_start] + '{desc}' + chunk[desc_end:]
                    _log.debug("add Python method '{}'".format(name))
                    methods[name] = chunk
                else:
                    if 'abstractmethod' in chunk:
                        _log.warn('Failed to match method: {}'
                                  .format(str_prefix(chunk, 280)))
                if name:
                    methods[name] = chunk
                chunk = ''
            else:
                chunk += line

    _log.debug('Python methods found: {}'.format(methods.keys()))

    return methods

DESCRIPTION_RE = re.compile('''
\s*/\*\*(.*?)        # Comment start
(?:\.\\n|\\n\\n).*?  # end of description
\*/\s*\\n            # Comment end
\s*[a-zA-Z0-9_<>,]+\s+(\w+)\s*\(.*   # Method declaration
''', flags=re.X | re.M | re.S)

def extract_descriptions(src):
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

def insert_python(src, tgt, strm=sys.stdout):
    _log.info("Insert: from={src} target={tgt} language=Python"
              .format(src=src, tgt=tgt))
    descriptions = extract_descriptions(src)
    methods = extract_python_methods(tgt)
    formatted_methods = {}
    for key, desc in descriptions.iteritems():
        if not key in methods:
            _log.warn('Description for method {m} has no match in Python'
                      .format(m=key))
        else:
            formatted_methods[key] = methods[key].format(desc=desc)
    for name in sorted(methods.keys()):
        if name in formatted_methods:
            strm.write(formatted_methods[name])
        else:
            strm.write(methods[name].format(desc='Description goes here'))
        strm.write('\n')

def get_target_method(tgt):
    ext_dot = tgt.rfind('.')
    if ext_dot == -1 or ext_dot == len(tgt) - 1:
        return None
    target_ext = tgt[ext_dot + 1:]
    if target_ext not in SOURCE_EXT:
        return None
    if target_ext == 'py':
        return insert_python

def main(cmdline):
    cwd = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='Source .thrift file')
    parser.add_argument('target', help='Target source code file. Type is '
                                       'determined by file extension.')
    parser.add_argument('--verbose', '-v', dest='vb', action="count", default=0,
                        help="Print more verbose messages to standard error. "
                             "Repeatable. (default=ERROR)")
    args = parser.parse_args(cmdline)
    verbosity = (logging.ERROR, logging.WARNING, logging.INFO,
                 logging.DEBUG)[min(args.vb, 3)]
    _log.setLevel(verbosity)

    meth = get_target_method(args.target)
    if meth is None:
        source_ext_list = ', '.join(SOURCE_EXT)
        parser.error('Target file must end in a recognized extension: {}'
                     .format(source_ext_list))

    meth(args.source, args.target)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))