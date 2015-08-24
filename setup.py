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
    "packages": ["biokbase",
                 "biokbase.data_api",
                 "biokbase.data_api.genome",
                 "biokbase.data_api.tests",
                 "biokbase.data_api.tests.performance",
                 "biokbase.workspace"],
    "scripts": ["bin/data_api_test_basic.py", 
                "bin/data_api_demo.py", 
                "bin/data_api_benchmark.py" , 
                "bin/data_api_test_genome_annotation_api.py"],
    "name": "genome_api"
}

setuptools.setup(package_dir = {'': 'lib'},
                 test_suite = "biokbase.data_api.tests.basic_suite",
                 **config)
