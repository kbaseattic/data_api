[![Join the chat at https://gitter.im/kbase/data_api](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/kbase/data_api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# data_api

Towards a unified data api for KBase

This repository is configured to use TravisCI

Source code is under lib/ (Python)
[![Build Status](https://travis-ci.org/kbase/data_api.svg?branch=master)](https://travis-ci.org/kbase/data_api)
[![Coverage Status](http://codecov.io/github/kbase/data_api/coverage.svg?branch=master)](http://codecov.io/github/kbase/data_api?branch=master)

#quickstart instructions

1. install virtualenv using your local installer
e.g., apt-get install virtualenv

2. create a virtualenv environment to install the source to 
e.g., virtualenv venv

3. activate the virtualenv
e.g., source venv/bin/activate

4. pip install this package to your virtualenv
e.g., pip install data_api/

5. set your KB_AUTH_TOKEN to your token string
e.g., in a KBase environment use kbase-login to retrieve a token, check your .kbase_config

6. run nosetests doekbase.data_api to verify your install is working

You can run pip install data_api/ --upgrade if you have edited files
locally and want to test them out without having to reset the virtualenv.

You can get out of the virtualenv environment with "deactivate".

# Examples

Example IPython (Jupyter) notebooks are in examples/notebooks. To run, follow installation instructions above, then

    ipython notebook examples/notebooks/data_api-display.ipynb 
    
You can also view these notebooks on github.

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

The full test suite requires either a network connection and authorization for the KBase Workspace and Shock, or a local copy of test data for use by the file-based workspace and Shock implementations. Even if you have network access and auth tokens, the file-based tests may be preferable because they are faster, self-consistent, and do not add any load to the services. The test data does require one extra setup step, described here.

The test data, because it is big and not code, is separated from the main `data_api` repo. It is stored in a git submodule called `data_api_test_resources`. Please refer to the [Git submodule documentation](http://git-scm.com/docs/git-submodule) for details, but the basic commands that you should make sure you do to get the most recent version of the submodules are:

1. In a repository that does not yet have any copy of the `data_api_test_resources` sub-repo, to initialize and clone the repo:

        git submodule init
  
2. In a repository that does have a copy of the cloned repo, to update to the latest version:

        git submodule update
    
The sub-repository will be cloned in the directory `test_resources`.