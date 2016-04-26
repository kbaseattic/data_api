"""
Pre-process Thrift scripts

This processes include statements of the form:

#%include foobar foo/bar.thrift

"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '4/5/16'

import logging

_log = logging.getLogger('kbase.preprocess')
import os
import re

class ThriftPPException(Exception):
    pass

class FileNotFound(ThriftPPException):
    pass

class IncludedFileNotFound(ThriftPPException):
    def __init__(self, source, filename, linenum):
        msg = 'Cannot find file "{}" included from {}:{}'.format(filename, source, linenum)
        ThriftPPException.__init__(self, msg)

class ThriftPP(object):
    """Thrift pre-processor.
    """
    INC_START = re.compile('#\s*%include\s+(\S+)')
    INC_END_PREFIX = '#%endinclude'
    INC_END = re.compile(INC_END_PREFIX)
    INC_END_MARKER = INC_END_PREFIX + ' {label}'

    def __init__(self, include_paths=None, read_file=None, write_file=None, included=None):
        """Create, but do not scan paths and files until :meth:`process` is called.

        Args:
            include_paths (list[str]): Paths for included files
            read_file (file): Input file
            write_file (file): Output file (may be same object as read_file)
            included (set): Already included paths (to avoid loops)
        Raises:
            ThriftPPException if thrift_file is empty
        """

        self._paths = include_paths or os.getcwd()
        self._rfile, self._wfile = read_file, write_file
        self._included = included or set()
        self._included.add(read_file.name)
        self._files_changed = set()

    def process(self):
        """Process thrift file and include paths.

        Returns:
            True if changed, False otherwise

        Raises:
            IOError if main file cannot be opened
            IncludedFileNotFound if included file cannot be opened
        """
        if self._rfile.closed:
            raise IOError('Input file {} is closed'.format(self._rfile.name))

        contents = self._scan()
        new_contents = self._update(contents)
        changed = contents != new_contents
        if changed or self._rfile is not self._wfile:
            self._replace(new_contents)
            self._files_changed.add(self._wfile.name)
        return changed

    def close(self):
        """Close all open files.
        """
        self._rfile.close()
        self._wfile.close()

    def get_changed_files(self):
        """Get list of all files changed, directly or indirectly.
        """
        return list(self._files_changed)

    def _scan(self):
        return [s.strip() for s in self._rfile.readlines()]

    def _update(self, lines):
        """Update the contents.
        This processes any includes.

        Raises:
            IncludedFileNotFound
        """
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            result.append(line)
            _log.debug('process line="{}"'.format(line))
            # look for a special include-start line
            match = self.INC_START.match(line)
            if match:
                _log.debug('match line={}'.format(line))
                filename = match.group(1)
                label = '{}'.format(filename)
                # read replacement from the file
                try:
                    replacement = self._read_include(filename)
                except FileNotFound:
                    raise IncludedFileNotFound(self._rfile.name, filename, i+1)
                result.extend(replacement)
                # look for end of included section
                end_pos = self._find_end(label, lines, i + 1)
                if end_pos > 0:
                    _log.debug("skip to={}".format(end_pos))
                    # if found, jump past older version of include
                    i = end_pos
                else:
                    # append an end marker for next time
                    result.append(self.INC_END_MARKER.format(label=label))
                    i += 1
            else:
                # move to next line of input
                i += 1
        return result

    def _read_include(self, filename):
        if filename in self._included:
            _log.warn('circular-include file={}'.format(filename))
            return []
        # recursively include
        path = self._find_included_file(filename)
        if path is None:
            raise FileNotFound(filename)
        fp = file(path, 'r+')
        child_inc = ThriftPP(include_paths=self._paths, read_file=fp,
                             write_file=fp, included=self._included)
        changed = child_inc.process()
        if changed:
            self._files_changed.add(path)
        child_inc.close()
        # return include-processed file, dropping include/end-include markers
        lines = []
        for line in file(path).readlines():
            if not (self.INC_START.match(line) or self.INC_END.match(line)):
                lines.append(line.strip())
        return lines

    def _find_included_file(self, filename):
        if os.path.exists(filename):
            return filename
        if not os.path.isabs(filename):
            for include_path in self._paths:
                inc_filename = os.path.join(include_path, filename)
                if os.path.exists(inc_filename):
                    return inc_filename
        return None

    def _find_end(self, label, lines, pos):
        pattern = re.compile(self.INC_END_MARKER.format(label=label))
        i = pos
        found = -1
        while i < len(lines):
            if pattern.match(lines[i]):
                found = i
                break
            i += 1
        return found

    def _replace(self, lines):
        if self._wfile.closed:
            raise IOError('Output file {} is closed'.format(self._wfile.name))
        if self._rfile is self._wfile:
            self._wfile.seek(0)
            self._wfile.truncate()
        for line in lines:
            self._wfile.write(line + '\n')

## tests


def test_basic():
    print("Run test_basic")
    if not os.path.exists('foo.txt'):
        f = open('foo.txt', 'w')
        for s in ['line 1', 'line 2', '//%include foo', 'line 3']:
            f.write(s + '\n')
        f.close()
    f = open('foo.txt', 'r+')
    pp = ThriftPP(read_file=f, write_file=f)
    pp.process()
    f.seek(0)
    for i, line in enumerate(f):
        print("{:3d}: {}".format(i + 1, line[:-1]))
    pp.close()