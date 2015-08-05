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
    "install_requires": [
        "Jinja2==2.7.3",
        "Sphinx==1.3.1",
        "guzzle-sphinx-theme==0.7.2",
        "nose",
        "python-coveralls",
        "six==1.9.0",
        "enum34",
        "pandas==0.16.2",
        "qgrid==0.1.1",
        "matplotlib==1.4.3",
        "requests==2.7.0",
        "notebook==4.0.1"
    ],
    "packages": ["biokbase","biokbase.data_api","biokbase.data_api.tests","biokbase.workspace"],
    "scripts": ["bin/data_api_test_basic.py", "bin/data_api_demo.py"],
    "name": "genome_api"
}

setuptools.setup(package_dir = {'': 'lib'},
                 test_suite = "biokbase.data_api.tests.basic_suite",
                 **config)
