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
PYTHON_FUNC_RE = re.compile('def ([a-z_]+)\(')

# Classes and functions

class Method(object):
    """Method in the target source file.

    Expect the body to contain a Python-style formatting
    template, `{desc}`, that will be replaced with the
    description from the Thrift file.
    """
    def __init__(self, name, body):
        self.name = name
        self._body = body

    def set_desc(self, text):
        self._body = self._body.format(desc=text)

    def dump(self, strm):
        strm.write(self._body)
        strm.write('\n')

def extract_python_methods(src):
    """Extract method bodies from Python file.

    Args:
      src (str): Name of source code file
    Returns:
      dict<str,str>: Mapping of method names to descriptive text
    """
    methods = {}
    with open(src, 'r') as f:
        name, body, expect_desc, comment_block = None, None, False, False
        for line in f:
            txt = line.strip()
            _log.debug("PYTHON ({}) {}".format(name, txt))
            # If we are currently processing a method block..
            if name is not None:
                # Name being empty means we still need to get
                # the actual function name itself. After this,
                # we expect the description.
                if name == '':
                    m = PYTHON_FUNC_RE.match(txt)
                    if m is None:
                        _log.error('Expected Python function in: {}'
                                   .format(txt))
                        raise ValueError('Parse error in {}'.format(src))
                    name = m.group(1)
                    expect_desc = True
                    body += line
                # If we are past the desc, but still in the comment
                # block, then look for the end of that block.
                # Any other text in the docstring should be escaped so
                # template '{}' characters are not accidentally added.
                elif comment_block:
                    s = line.replace('{', '{{').replace('}', '}}')
                    body += s
                    if txt.endswith('"""'):
                        comment_block = False
                        expect_desc = False
                    elif expect_desc and (txt.endswith('.') or len(line) == 0):
                        expect_desc = False
                # If we processed the method name, but haven't handled the
                # docstring yet, then handle it. The initial description of
                # the docstring will be replaced with a single placeholder
                # variable name.
                elif expect_desc:
                    if txt.startswith('"""'):
                        body += '    """{desc}\n'
                        comment_block = True
                # A blank line signals the end of the method block.
                # Create a new entry in the methods mapping and reset
                # the state.
                elif len(txt) == 0:
                    methods[name] = Method(name, body)
                    name = None # reset
                    expect_desc, comment_block = False, False
            # Otherwise check to see if this is the start of a
            # new method block. If so, start the processing. Otherwise,
            # ignore the line.
            elif txt.startswith('@abc.abstractmethod'):
                body = line
                name = ''
    return methods

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
    last_desc, expect_desc = None, False
    with open(src, 'r') as f:
        for line in f:
            # If we are processing a description, then add
            # this line to the description. If this line is
            # blank or ends in a period or doesn't start with a
            # comment '*', then stop processing a description.
            if expect_desc:
                line = line.strip()
                if line[0] != '*':
                    expect_desc = False
                else:
                    text = line[1:].strip()
                    if len(text) == 0:
                        expect_desc = False
                    else:
                        if last_desc is None:
                            last_desc = ''
                        else:
                            last_desc += ' '
                        last_desc += text
                        if text.endswith('.'):
                            expect_desc = False
                continue

            # If we are not processing a description, then
            # check for a Thrift function declaration. If this is
            # found, then record the matching description and
            # reset the description to be empty.
            m = THRIFT_FUNC_RE.match(line)
            if m is not None:
                method_name = m.group(1)
                if last_desc is not None:
                    descriptions[method_name] = last_desc
                    last_desc = None
                else:
                    _log.warn('Undocumented thrift function: {f}'
                              .format(f=method_name))
                continue

            # If neither a description nor a method, then check if this
            # is the start of a description block. Otherwise, do nothing.
            if line.strip().startswith('/**'):
                expect_desc = True

    return descriptions

def insert_python(src, tgt):
    _log.info("Insert: from={src} target={tgt} language=Python"
              .format(src=src, tgt=tgt))
    descriptions = extract_descriptions(src)
    methods = extract_python_methods(tgt)
    for key, desc in descriptions:
        if not key in methods:
            _log.warn('Description for method {m} has no match in Python'
                      .format(m=key))
        else:
            methods[key].set_desc(desc)
    for name in sorted(methods.keys()):
        methods[name].dump(sys.stdout)

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
    verbosity = (logging.ERROR, logging.INFO, logging.DEBUG)[min(args.vb, 2)]
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