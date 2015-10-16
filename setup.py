import setuptools
import logging
import os
import sys

# Logging

logging.basicConfig()
_log = logging.getLogger('setup')

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
        packages = list()
    
        with open(filename, 'r') as req_file:
            req_lines = req_file.read().splitlines()
        
            for line in req_lines:
                if line.strip() == "":
                    pass
                elif line.startswith("-r"):
                    packages.extend(parse_requirements(line.split(" ")[-1]))
                else:
                    packages.append(line)
        return packages

    setup_args = sys.argv[1:]

    if g_with_jupyter:
        install_requires = parse_requirements(
            os.path.join(os.path.dirname(__file__),"requirements-jupyter.txt"))
    else:
        _log.warn("--jupyter not specified, so using minimal install "
                  "without packages in doekbase.data_api.interactive")
        packages.remove('doekbase.data_api.interactive')
        install_requires = parse_requirements(
            os.path.join(os.path.dirname(__file__),"requirements.txt"))

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
                "bin/dump_wsfile"],
    "name": "doekbase_data_api",
    "entry_points": {
        'nose.plugins.0.10': [
            'wsurl = doekbase.data_api.tests.nose_plugin_wsurl:WorkspaceURL'
        ]
    },
    "zip_safe": True
}

setuptools.setup(package_dir = {'': 'lib'},
                 script_args=filter_args(),
                 install_requires=get_dependencies(),
                 **config)
