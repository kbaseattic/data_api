[![Join the chat at https://gitter.im/kbase/data_api](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/kbase/data_api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# data_api

Towards a unified data api for KBase

This repository is configured to use TravisCI

Source code is under lib/ (Python)
[![Build Status](https://travis-ci.org/kbase/data_api.svg?branch=master)](https://travis-ci.org/kbase/data_api)
[![Coverage Status](https://coveralls.io/repos/kbase/data_api/badge.svg?branch=master)](https://coveralls.io/r/kbase/data_api?branch=master)

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

6. run nosetests biokbase.data_api to verify your install is working

You can run pip install data_api/ --upgrade if you have edited files
locally and want to test them out without having to reset the virtualenv.

You can get out of the virtualenv environment with "deactivate".

# Examples

Example IPython (Jupyter) notebooks are in examples/notebooks. To run, follow installation instructions above, then

    ipython notebook examples/notebooks/data_api-display.ipynb 
    
You can also view these notebooks on github.
