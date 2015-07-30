import setuptools

config = {
    "description": "KBase Data API",
    "author": "Matt Henderson",
    "url": "https://github.com/kbase/data_api/",
    "download_url": "https://github.com/kbase/data_api/stuff?download",
    "author_email": "mhenderson@lbl.gov",
    "version": "0.1",
    "setup_requires": ["six"],
    "tests_require": ["nose"],
    "install_requires": ["falcon", "requests", "six"],
    "packages": ["biokbase","biokbase.data_api","biokbase.data_api.tests","biokbase.workspace"],
    "scripts": ["bin/data_api_test_basic.py"],
    "name": "genome_api"
}

setuptools.setup(package_dir = {'': 'lib'},
                 test_suite = "biokbase.data_api.tests.basic_suite",
                 **config)
