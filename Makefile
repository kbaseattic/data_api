SERVICE = data_api
SERVICE_CAPS = dataApi
LIB_DIR = lib
SCRIPTS_DIR = scripts
LBIN_DIR = bin
TARGET ?= /kb/deployment
SERVICE_DIR ?= $(TARGET)/services/$(SERVICE)
EXECUTABLE_SCRIPT_NAME = run_$(SERVICE_CAPS)_async_job.sh
STARTUP_SCRIPT_NAME = start_service
KB_RUNTIME ?= /kb/runtime
ANT = $(KB_RUNTIME)/ant/bin/ant

default: deploy

# not really sure what to do with this target yet
deploy-client: 

deploy: deploy-lib deploy-service-scripts

deploy-lib:
	rm -rf $(SERVICE_DIR)/venv
	virtualenv $(SERVICE_DIR)/venv
	. $(SERVICE_DIR)/venv/bin/activate && pip install .

test: subupdate shutdown startup
	@echo '+- Run nosetests from the data_api source directory, which will use the test data'
	KB_DEPLOY_URL=dir_nocache nosetests -c nose.cfg -c nose-local.cfg

subupdate:
	@echo 'Update submodule in test_resources, that has local data'
	@echo 'This command will either execute very quickly, or take minutes..'
	git submodule update --remote --merge
