try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def parse_reqs(reqs):
    f = open(reqs)
    return [l.strip('\n') for l in f if l.strip('\n') and not l.startswith('#')]

config = {
        'description': 'KBase nextgen data API: workspace-to-graph experiments',
    'author': 'Dan Gunter',
    'url': 'https://github.com/kbase/nextgen',
    'download_url': 'https://github.com/kbase/nextgen',
    'author_email': 'dkgunter@lbl.gov',
    'version': '0.1',
    'install_requires': parse_reqs('requirements.txt'),
    'packages': ['wsgraph'],
    'scripts': [],
    'name': 'kbase_data_api_ws_to_graph'
}

setup(**config)
