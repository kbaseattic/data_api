import setuptools
import os
import sys

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

version = open('VERSION').read().strip()
packages = setuptools.find_packages("lib")
setup_args = sys.argv[1:]

if "--jupyter" in setup_args:
    setup_args.remove("--jupyter")
    install_requires = parse_requirements(
        os.path.join(os.path.dirname(__file__),"requirements-jupyter.txt"))
else:
    install_requires = parse_requirements(
        os.path.join(os.path.dirname(__file__),"requirements.txt"))

config = {
    "description": "KBase Data API",
    "author": "Matt Henderson",
    "url": "https://github.com/kbase/data_api/",
    "download_url": "https://github.com/kbase/data_api/stuff?download",
    "author_email": "mhenderson@lbl.gov",
    "version": version,
    "setup_requires": ["six"],
    "install_requires": install_requires,
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
                 script_args=setup_args,
                 **config)
