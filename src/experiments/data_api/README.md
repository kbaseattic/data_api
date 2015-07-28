#quickstart instructions

1. install virtualenv using your local installer
e.g., apt-get install virtualenv

2. create a virtualenv environment to install the source to 
e.g., virtualenv venv

3. activate the virtualenv
e.g., source venv/bin/activate

4. pip install this package to your virtualenv
e.g., pip install data_api/src/experiments/data_api/

5. set your KB_AUTH_TOKEN to your token string
e.g., in a KBase environment use kbase-login to retrieve a token, check your .kbase_config

6. run data_api_basic_test.py to verify your install is working

You can run pip install data_api/src/experiments/data_api/ --upgrade if you have edited files
locally and want to test them out without having to reset the virtualenv.

You can get out of the virtualenv environment with "deactivate".
