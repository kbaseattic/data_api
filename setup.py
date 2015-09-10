import setuptools

def parse_requirements():
    packages = list()
    
    with open("requirements.txt", 'r') as req_file:
        req_lines = req_file.read().splitlines()
        
        for line in req_lines:
            if line.strip() == "" or line.startswith("-"):
                pass
            else:
                packages.append(line)
    return packages

config = {
    "description": "KBase Data API",
    "author": "Matt Henderson",
    "url": "https://github.com/kbase/data_api/",
    "download_url": "https://github.com/kbase/data_api/stuff?download",
    "author_email": "mhenderson@lbl.gov",
    "version": "0.1",
    "setup_requires": ["six"],
    "tests_require": ["nose"],
    "install_requires": parse_requirements(),
    "packages": ["doekbase",
                 "doekbase.data_api",
                 "doekbase.data_api.annotation",
                 "doekbase.data_api.sequence",
                 "doekbase.data_api.taxonomy",
                 "doekbase.data_api.taxonomy.taxon",
                 "doekbase.data_api.taxonomy.taxon.service",
                 "doekbase.data_api.genome",
                 "doekbase.data_api.baseobj",
                 "doekbase.data_api.tests",
                 "doekbase.data_api.tests.performance",
                 "doekbase.workspace"],
    "scripts": ["bin/data_api_demo.py",
                "bin/data_api_benchmark.py"],
    "name": "doekbase_data_api"
}

setuptools.setup(package_dir = {'': 'lib'},
                 test_suite = "doekbase.data_api.tests.test_suite_basic",
                 **config)
