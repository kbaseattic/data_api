**Version**: 0.1.0
 
[![Join the chat at https://gitter.im/kbase/data_api](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/kbase/data_api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

<img src="GolgiVolvox.png" alt="Volvox" style="width: 100px;"/>

# data_api

Towards a unified data api for KBase

This repository is configured to use TravisCI.

Source code is under lib/ (Python) and jslib/ (JavaScript)

Master branch status
[![Build Status](https://travis-ci.org/kbase/data_api.svg?branch=master)](https://travis-ci.org/kbase/data_api)
[![Coverage Status](http://codecov.io/github/kbase/data_api/coverage.svg?branch=master)](http://codecov.io/github/kbase/data_api?branch=master)
![Coverage Graph](http://codecov.io/github/kbase/data_api/branch.svg?branch=master&time=1y)

Develop branch status
[![Build Status](https://travis-ci.org/kbase/data_api.svg?branch=develop)](https://travis-ci.org/kbase/data_api)
[![Coverage Status](http://codecov.io/github/kbase/data_api/coverage.svg?branch=develop)](http://codecov.io/github/kbase/data_api?branch=master)
![Coverage Graph](http://codecov.io/github/kbase/data_api/branch.svg?branch=develop&time=1y)

##### Table of Contents
- [Quickstart install instructions](#quickstart-instructions-for-installation)
- [Documentation](#documentation)
- [Examples](#examples)
- [Information for developers modifying Data API](#for-developers)


#Quickstart instructions for installation

1. Clone data_api repo:

        git clone https://github.com/kbase/data_api/

2. Install virtualenv and python development libraries using your local installer:

   **Note:** KBase currently only supports Python 2.7.X

   - Linux
       * Debian/Ubuntu:

                apt-get install python-dev python-virtualenv
        
       * Redhat/CentOS: 

                yum install python-devel
                pip install virtualenv

   - OS X:
      * Homebrew: 

                brew install python python-config
                pip install virtualenv

      * Macports: 

                port install python
                pip install virtualenv

3. Create a virtualenv environment to install the source to:
        
        virtualenv venv

4. Activate the virtualenv:

    **Note:** You can exit the virtualenv shell when you are finished using data_api with `deactivate`.

        source venv/bin/activate

5. pip install this package to your virtualenv:

        pip install data_api

6. If you installed data_api in a KBase environment, set your `KB_AUTH_TOKEN` to your token string.
   If you are installing to a non-KBase environment, you will need to get your token elsewhere and set it manually.
       * From a Narrative code cell:

            import os
            token = os.environ.get("KB_AUTH_TOKEN")

       * In an installed KBase shell environment:

            kbase-login
            #check your `.kbase_config` to make sure you obtained a token.
            cat ~/.kbase_config
            #now store your token in the shell environment
            export KB_AUTH_TOKEN=$(kbase-whoami -t)

# Documentation

[API docs](http://kbase.github.io/docs-ghpages/docs/data_api/index.html)

# Examples

Example IPython (Jupyter) notebooks are in examples/notebooks. 
To install ipython/jupyter dependencies for the examples:

    pip install -r data_api/requirements-jupyter.txt

**Note:** This step requires the installation of large packages such as numpy,
and can take many tens of minutes to complete.

You can view examples using a local ipython/jupyter notebook:

    ipython notebook examples/notebooks/data_api-display.ipynb 
    
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
network access and auth tokens, the file-based tests may be preferable because they are faster, self-consistent, 
and do not add any load to the services. The test data does require one extra setup step, described here.

The test data, because it is big and not code, is separated from the main `data_api` repo. 
It is stored in a git submodule called `data_api_test_resources`. Please refer to the 
[Git submodule documentation](http://git-scm.com/docs/git-submodule) for details, but the basic 
commands that you should make sure you do to get the most recent version of the submodules are:

**Note:** These steps assume that you are in the data_api git directory.

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
   
   - Linux
       * Debian/Ubuntu:

            apt-get install redis

       * Redhat/CentOS:

            yum install redis

   - OS X:
      * Homebrew:

            brew install redis

      * Macports:

            port install redis
   
   For other operating systems, see the Redis [homepage](http://redis.io)
   
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
   
   - **prod**        : KBase production environment, production Redis instance
   - **next**        : KBase next environment, next Redis instance
   - **ci**          : KBase continuous integration environment (Jenkins), CI Redis instance
   - **localhost**   : A local instance of KBase (docker or vm), assume local Redis caching
   - **dir_cache**   : Use local test files, assume local Redis caching
   - **dir_nocache** : Use local test files, do not attempt to cache using Redis

### Service logging

The Data API service logging is controlled by a file named, by default, "logging.conf", in the same directory as the configuration file from the `--config` option. You can choose another file with the `--log-config` option. If no explicit configuration is given, and the default file is not present, some basic default logging configuration will be used. Failure to open or parse a file provided with the `--log-config` option will cause the program to stop and exit.

For example:

* `data_api_start_service.py --service genome_annotation --config deployment.cfg` will look for a file `logging.conf` in the current directory.
* `data_api_start_service.py --service genome_annotation --config deployment.cfg --log-config ./logging.conf` is equivalent to the previous command.
* `data_api_start_service.py --service genome_annotation --config deployment.cfg --log-config /tmp/logging-test/logging.yaml` will configure logging from the named file in "/tmp/logging-test" instead of looking for "logging.conf" in the current directory. If that file does not exist, the program will stop with an error.

The configuration file is formatted using either the (older) ConfigParser format used by `logging.config.fileConfig` or the (newer) YAML format that is parsed and fed to `logging.config.dictConfig`; the format is auto-detected via trial and error. See the [logging.config module](https://docs.python.org/2.7/library/logging.config.html) documentation for details on the formats of these files. The `logging.conf` example in the root of the repository demonstrates how to configure output to a file and console, and control the level of logging for each service.

The output log format is largely controlled by the configuration file. Some of the messages have additional standardized formatting applied to the part in the `%(message)s` format code, i.e. the free-form string part of the log message. This standardized formatting is encoded the `doekbase.util.log_{event,start,end}` functions. (Note: This formatting can be altered, too, by changing the global `_MESSAGE_FORMAT` dict of the module; but this is not recommended). The basic idea is to reduce the free-form part to a simple name for the event, and put everything else in key/value pairs with a standard format. Also, messages at the beginning and the end of something (in cases where that makes sense) should be named so that they are easily matched. For example, the pair of log messages for the service starting and stopping look like this:

        2016-02-18 05:34:39,260 [INFO] doekbase.data_api.annotation.genome_annotation.service.driver: start_service.begin | host='',port=9103
        # ...
        2016-02-18 05:35:01,910 [INFO] doekbase.data_api.annotation.genome_annotation.service.driver: start_service.end (22.649431) | host='',port=9103

Note the '.begin' and '.end' event suffixes, as well as the "|" separating the message into name from the key/value pairs of the values. The number in parentheses on the '.end' event is the duration in seconds since the corresponding '.start'. For a message that is not part of a begin/end pair, the format is the same:

        2016-02-18 05:34:39,137 [INFO] doekbase.data_api_start_service: activating REDIS | host=localhost,port=6379

Not all, in fact right now not even most, of the messages from the services have this standard format extension. But the goal is to slowly convert them. (We'll see how that goes!)

## Testing 

   To verify all Data API code with local tests.

   Change to the source directory:

    cd data_api
   
   Install the [Test data](README.md#test-data)

   Start each of the API services:
   
    data_api_start_service.py --config deployment.cfg --service taxon --port 9101 &
    data_api_start_service.py --config deployment.cfg --service assembly --port 9102 &
    data_api_start_service.py --config deployment.cfg --service genome_annotation --port 9103 &

   Run nosetests from the data_api source directory, which will use the test data:

    nosetests -c nose.cfg -c nose-local.cfg -s doekbase.data_api

### JavaScript tests

For the JavaScript API, all the code and tests live under `jslib`. See the README in that directory for more details.


### Example narratives

	Retrieving and counting genomic features with a local data API client for a [GenomeAnnotation object] (https://narrative-ci.kbase.us/narrative/ws.3413.obj.1)
	Retrieving and counting genomic features with direct data API access for a [GenomeAnnotation object] (https://narrative-ci.kbase.us/narrative/ws.3292.obj.1)
	A [table] of genome properties for all genomes belonging to a taxon (https://narrative-ci.kbase.us/narrative/ws.3524.obj.1)
	Panel of data quality plots for [GenomeAnnotation and Assembly objects] (https://narrative-ci.kbase.us/narrative/ws.3413.obj.1)
