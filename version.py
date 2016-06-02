#!/usr/bin/env python
"""
Manipulate project versions

Examples:
  version.py bump # increment bugfix 0.1.2 -> 0.1.3
  version.py bump --minor # increment minor version 0.1.2 -> 0.2.0
  version.py bump --major # increment major version 0.1.2 -> 1.0.0
  version.py show # show current version
  version.py history # extract version history from CHANGELOG and show it, latest first
  version.py history --asc # extract version history from CHANGELOG and show it, earliest first
  
Files affected:
  VERSION - this is where the version number is changed
"""
# Stdlib
import argparse
import os
import re
#import six
import shutil
import sys

curdir = os.path.dirname(sys.argv[0])
version_file = os.path.join(curdir, 'VERSION')
changelog_file = os.path.join(curdir, 'CHANGELOG')
install_locations = {
    'python':
        { 'lib/doekbase/data_api/core.py': 'DATA_API_VERSION' }
}
def install():
    """Install version
    """
    version = _get_version()
    #for module_path, variable in six.iteritems(install_locations['python']):
    for module_path, variable in install_locations['python'].iteritems():
        pattern = '^\s*{}\s*=\s*[\'"].*[\'"]\s*'.format(variable)
        #print("pattern = {}".format(pattern))
        re_pattern = re.compile(pattern)
        replacement = '{} = "{}"\n'.format(variable, version)
        path = os.path.join(curdir, module_path)
        tmp_path = path + '-tmp'
        shutil.copy(path, tmp_path)
        changes = 0
        with open(path) as input_file, open(tmp_path, 'w') as output_file:
            for line in input_file:
                if re_pattern.match(line):
                    modified_line = re.sub(pattern, replacement, line)
                    output_file.write(modified_line)
                    changes += 1
                else:
                    output_file.write(line)
        if changes > 0:
            shutil.move(tmp_path, path)
            print("version updated in {infile}: {ver}".format(infile=path, ver=version))
        else:
            print("version unchanged in {infile}: {ver}".format(infile=path, ver=version))
            os.unlink(tmp_path)

def show():
    """Show (print) current version, from main version file.
    """
    print(_get_version())

def _get_version():
    return open(version_file).read().strip()

def history(ascending=False):
    """Show (print) version history, extracted from Changelog.
    """
    clog_re = '\s*##\s*\[(\d+\.\d+\.\d+)\]\s*-?\s*(\d\d\d\d-\d\d-\d\d)'
    clog = open(changelog_file)
    # gather
    releases = {}
    for line in clog:
        m = re.match(clog_re, line.strip())
        if m:
            version, release_date = m.group(1), m.group(2)
            if release_date in releases:
                releases[release_date].append(version)
            else:
                releases[release_date] = [version]
    # sort
    dates = releases.keys()
    dates.sort(reverse=not ascending)
    # print
    for date in dates:
        for version in sorted(releases[date]):
            print('{}\t{}'.format(date, version))

def bump(major=False, minor=False):
    """Bump version.
    Pre: at most one of major, minor keyword args is True
    """
    # read and parse current version
    version_re = '(\d+)\.(\d+)\.(\d+)(-?\w*)'
    old_version = _get_version()
    m = re.match(version_re, old_version)
    if not m:
        raise ValueError('Invalid version in {}: {}'.format(version_file, old_version))
    v_major, v_minor, v_bug, bugmod =  int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    # create new version
    if major:
        v_major += 1
        v_minor, v_bug = 0, 0
    elif minor:
        v_minor += 1
        v_bug = 0
    else:
        v_bug += 1
    new_version = '{}.{}.{}'.format(v_major, v_minor, v_bug)
    # update main version file
    f = open(version_file, 'w')
    f.write(new_version)
    f.close()

def main():
    p = argparse.ArgumentParser(description=__doc__.strip().split('\n')[0], 
                                epilog=__doc__[__doc__.find('Examples'):],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', help='Command: install, bump, show, or history')
    p.add_argument('--major', action='store_true', dest='bump_major', help='Do a major version bump')
    p.add_argument('--minor', action='store_true', dest='bump_minor', help='Do a minor version bump')
    p.add_argument('--asc', action='store_true', dest='history_asc', help='Show history with earliest first')
    args = p.parse_args()
    command = args.command.lower()
    try:
        if command == 'install':
            install()
        elif command == 'bump':
            if args.bump_major and args.bump_minor:
                p.error('Cannot bump both major and minor versions at the same time. Pick one.')
            bump(major=args.bump_major, minor=args.bump_minor)
        elif command == 'show':
            show()
        elif command == 'history':
            history(ascending=args.history_asc)
        else:
            raise ValueError('Command must be bump, show, or history')
    except Exception as err:
        p.error('Command {} failed: {}'.format(command, err))
        return -1
    return 0
    
if __name__ == '__main__':
    sys.exit(main())
        
