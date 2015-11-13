[![Join the chat at https://gitter.im/kbase/data_api](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/kbase/data_api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

<img src="GolgiVolvox.png" alt="Volvox" style="width: 100px;"/>

# data_api

Towards a unified data api for KBase

This repository is configured to use TravisCI

Source code is under lib/ (Python)

Master branch status
[![Build Status](https://travis-ci.org/kbase/data_api.svg?branch=master)](https://travis-ci.org/kbase/data_api)
[![Coverage Status](http://codecov.io/github/kbase/data_api/coverage.svg?branch=master)](http://codecov.io/github/kbase/data_api?branch=master)
![Coverage Graph](http://codecov.io/github/kbase/data_api/branch.svg?branch=master&time=1y)

Develop branch status
[![Build Status](https://travis-ci.org/kbase/data_api.svg?branch=develop)](https://travis-ci.org/kbase/data_api)
[![Coverage Status](http://codecov.io/github/kbase/data_api/coverage.svg?branch=develop)](http://codecov.io/github/kbase/data_api?branch=master)
![Coverage Graph](http://codecov.io/github/kbase/data_api/branch.svg?branch=develop&time=1y)

#quickstart instructions for installation

0. Clone data_api repo:

        git clone https://github.com/kbase/data_api/

1. Install virtualenv and python development libraries using your local installer:

        apt-get install python-dev python-virtualenv

2. Create a virtualenv environment to install the source to:
        
        virtualenv venv

3. Activate the virtualenv:

        source venv/bin/activate

4. pip install this package to your virtualenv:

        pip install data_api

   You can exit the virtualenv shell when you are finished using data_api with "deactivate".

5. If you installed data_api in a KBase environment, set your `KB_AUTH_TOKEN` to your token string.
   If you are installing to a non-KBase environment, you will need to get your token elsewhere and set it manually.
   You can retrieve a token from a Narrative code cell using the following:
   
        import os
        token = os.environ.get("KB_AUTH_TOKEN")

   In an installed KBase shell environment use `kbase-login` to retrieve a token.

        kbase-login

   Now check your `.kbase_config` to make sure you obtained a token.
    
        cat ~/.kbase_config
   
   Once you have a valid token, run this command in the bash shell:

        export KB_AUTH_TOKEN=$(kbase-whoami -t)

# Documentation

[API docs](http://kbase.github.io/docs-ghpages/docs/data_api/index.html)

# Examples

Example IPython (Jupyter) notebooks are in examples/notebooks. 
To install ipython/jupyter dependencies for the examples:

    pip install -r data_api/requirements-jupyter.txt

You can view examples using a local ipython/jupyter notebook:

    ipython notebook examples/notebooks/data_api-display.ipynb 
    
You can also view these notebooks from nbviewer.

[Simple Taxon example](http://nbviewer.ipython.org/github/kbase/data_api/blob/develop/examples/notebooks/see-taxon-run.ipynb)
[Genome data plots](http://nbviewer.ipython.org/github/kbase/data_api/blob/develop/examples/notebooks/plot_genome_data.ipynb)

# For developers

## Versioning and Changelog

Use semantic versioning, "x.y.z", where x is major, or incompatible, differences, y is new but backwards-compatible, and z is minor changes and bugfixes.

Keep the version current in the file `VERSION` at the root level.

Record changes in a human-readable format in the `CHANGELOG` at the root level. Each version should:

- List its release date in the above format.
- Group changes to describe their impact on the project, as follows:
    * Added for new features.
    * Changed for changes in existing functionality.
    * Deprecated for once-stable features removed in upcoming releases.
    * Removed for deprecated features removed in this release.
    * Fixed for any bug fixes.
    * Security to invite users to upgrade in case of vulnerabilities.
- Changes not yet released should be put in the "Unreleased" section at the top. This serves as a sort of preview of upcoming changes.

## Test data

The full test suite requires either a network connection and authorization for the KBase Workspace and Shock, 
or a local copy of test data for use by the file-based workspace and Shock implementations. Even if you have 
network access and auth tokens, the file-based tests may be preferable because they are faster, self-consistent, and do not add any load to the services. The test data does require one extra setup step, described here.

The test data, because it is big and not code, is separated from the main `data_api` repo. It is stored in a git submodule called `data_api_test_resources`. Please refer to the [Git submodule documentation](http://git-scm.com/docs/git-submodule) for details, but the basic commands that you should make sure you do to get the most recent version of the submodules are:

1. In a repository that does not yet have any copy of the `data_api_test_resources` sub-repo, to initialize and clone the repo:

        git submodule init
  
2. In a repository that does have a copy of the cloned repo, to update to the latest version:

        git submodule update
    
The sub-repository will be cloned in the directory `test_resources`.

## Caching with Redis

   There is a deployment.cfg file in the data_api source directory that contains several target deployment locations.
   By default, services and tests will use dir_nocache, which uses the local file test data and will not require or use caching.
   If you would like to test with caching enabled, you can set the KB_DEPLOY_URL environment variable to one of the targets
   in the deployment.cfg file, for instance dir_cache.  This sets the redis_host to localhost and the redis_port to the default port.
   You can edit this file to change settings before starting Redis and the Data API services.
   
   There is also a redis.conf file located in the data_api source directory for running with Redis locally.
   
   Installation of Redis:
   
        apt-get install redis
   
   Starting the Redis instance:
        
        redis-server redis.conf

## Starting the Data API services

   Services can be started using the data_api_start_service.py script, which is in your path from a virtualenv install.

        data_api_start_service.py --config deployment.cfg --service taxon --port 9101
        data_api_start_service.py --config deployment.cfg --service assembly --port 9102        

   You can add a --kbase_url argument to indicate which service targets and configs from deployment.cfg to use.
   For instance, to set the services to use local files and assume a running Redis instance:
   
        data_api_start_service.py --config deployment.cfg --service assembly --port 9102 --kbase_url=dir_cache        
   
   The available targets are:
   
   - prod        : KBase production environment, production Redis instance
   - next        : KBase next environment, next Redis instance
   - ci          : KBase continuous integration environment (Jenkins), CI Redis instance
   - localhost   : A local instance of KBase (docker or vm), assume local Redis caching
   - dir_cache   : Use local test files, assume local Redis caching
   - dir_nocache : Use local test files, do not attempt to cache using Redis
   

## Testing 

   To verify all Data API code with local tests.

   Change to the source directory:

        cd data_api
   
   Install the [Test data](README.md#test-data)

   Start each of the API services:
   
        nohup data_api_start_service.py --config deployment.cfg --service taxon --port 9101 & > taxonAPI.out
        nohup data_api_start_service.py --config deployment.cfg --service assembly --port 9102 & > assemblyAPI.out        

   Run nosetests from the data_api source directory, which will use the test data:

        nosetests -c nose.cfg -c nose-local.cfg -s doekbase.data_api

