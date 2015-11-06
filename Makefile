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

deploy: deploy-service-scripts deploy-lib

deploy-lib:
	rm -rf $(SERVICE_DIR)/venv
	virtualenv $(SERVICE_DIR)/venv
	. $(SERVICE_DIR)/venv/bin/activate && pip install .

deploy-service-scripts:
	cp $(SCRIPTS_DIR)/start_service $(SCRIPTS_DIR)/stop_service $(SERVICE_DIR)/

clean:
	echo not implemented
