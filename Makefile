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

# don't deploy anything in production yet
deploy: 

deploy-lib:

deploy-service-scripts:

test:

subupdate:

startup:

shutdown:

clean:
