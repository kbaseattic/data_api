"""
Setup script for data_api Python packages and scripts.
"""
import setuptools
import logging
import os
import subprocess
import sys

# Logging

#logging.basicConfig()
_log = logging.getLogger('setup')
_h = logging.StreamHandler()
_h.setFormatter(logging.Formatter('%(asctime)s %(levelname)-7s %(name)s: %('
                                  'message)s'))
_log.addHandler(_h)
vb = sum([len(a) - 1 if a.startswith('-v') else 0 for a in sys.argv[1:]])
_log.setLevel([logging.WARN, logging.INFO, logging.DEBUG][min(vb, 2)])

# Globals

version = open('VERSION').read().strip()
packages = setuptools.find_packages("lib")
g_with_jupyter = False

# Functions

def filter_args():
    global g_with_jupyter
    setup_args = sys.argv[1:]

    # TODO: Put this new option into --help output

    if "--jupyter" in setup_args:
        g_with_jupyter = True
        setup_args.remove("--jupyter")

    return setup_args


def get_dependencies():
    def parse_requirements(filename):
        pkg = list()
    
        with open(filename, 'r') as req_file:
            req_lines = req_file.read().splitlines()
        
            for line in req_lines:
                if line.strip() == "":
                    pass
                elif line.startswith("-r"):
                    pkg.extend(parse_requirements(line.split(" ")[-1]))
                else:
                    pkg.append(line)
        return pkg

    setup_args = sys.argv[1:]

    if g_with_jupyter:
        install_requires = parse_requirements(
            os.path.join(os.path.dirname(__file__),"requirements-jupyter.txt"))
        open(os.path.join(os.path.dirname(__file__),'exclude-tests.txt'), 'w').write('') # clear it
    else:
        _log.warn("--jupyter not specified, so using minimal install "
                  "without packages in doekbase.data_api.interactive")
        exclude_pkg = 'doekbase.data_api.interactive'

        global packages
        if exclude_pkg in packages:
            packages.remove(exclude_pkg)

        install_requires = parse_requirements(
            os.path.join(os.path.dirname(__file__),"requirements.txt"))
        open(os.path.join(os.path.dirname(__file__),'exclude-tests.txt'), 'w')\
            .write('lib/' + exclude_pkg.replace('.', '/'))
        # clear it

    _log.debug('Install requirements: {}'.format(install_requires))
    return install_requires

config = {
    "description": "KBase Data API",
    "author": "Matt Henderson",
    "url": "https://github.com/kbase/data_api/",
    "download_url": "https://github.com/kbase/data_api/stuff?download",
    "author_email": "mhenderson@lbl.gov",
    "version": version,
    "setup_requires": ["six"],
    "tests_require": ["nose", "nose-timer", "codecov"],
    "packages": packages,
    "scripts": ["bin/data_api_demo.py",
                "bin/data_api_benchmark.py",
                "bin/dump_wsfile",
                "bin/extract_thrift_docs"],
    "name": "doekbase_data_api",
    "entry_points": {
        'nose.plugins.0.10': [
            'wsurl = doekbase.data_api.tests.nose_plugin_wsurl:WorkspaceURL'
        ]
    },
    "zip_safe": True
}

def main():
    subprocess.check_call(['./version.py', 'install'])
    setuptools.setup(package_dir = {'': 'lib'},
                     script_args = filter_args(),
                     install_requires = get_dependencies(),
                     **config)
    return 0

if __name__ == '__main__':
    sys.exit(main())