SERVICE = dataapi
SERVICE_CAPS = dataApi
LIB_DIR = lib
SCRIPTS_DIR = scripts
LBIN_DIR = bin
TARGET ?= /kb/deployment
SERVICE_DIR ?= $(TARGET)/services/$(SERVICE)
EXECUTABLE_SCRIPT_NAME = run_$(SERVICE_CAPS)_async_job.sh
STARTUP_SCRIPT_NAME = start_server
KB_RUNTIME ?= /kb/runtime
ANT = $(KB_RUNTIME)/ant/bin/ant

default: deploy

deploy-client: deploy

deploy:
	rm -rf $(SERVICE_DIR)/venv
	virtualenv $(SERVICE_DIR)/venv
	. $(SERVICE_DIR)/venv/bin/activate && pip install -vvv .
	cp $(SCRIPTS_DIR)/$(STARTUP_SCRIPT_NAME) $(SERVICE_DIR)/
	rsync -avzP $(LBIN_DIR) $(SERVICE_DIR)/

clean:
	echo not implemented
