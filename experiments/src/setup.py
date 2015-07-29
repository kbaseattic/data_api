try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def parse_reqs(reqs):
    f = open(reqs)
    return [l.strip('\n') for l in f if l.strip('\n') and not l.startswith('#')]

config = {
    'description': 'KBase nextgen data api',
    'author': 'Dan Gunter',
    'url': 'https://github.com/kbase/nextgen',
    'download_url': 'https://github.com/kbase/nextgen',
    'author_email': 'dkgunter@lbl.gov',
    'version': '0.1',
    'install_requires': parse_reqs('requirements.txt'),
    'packages': ['data_api'],
    'scripts': [],
    'name': 'kbase_data_api'
}

setup(**config)
