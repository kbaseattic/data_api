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

deploy-service-scripts:
	cp $(SCRIPTS_DIR)/start_service $(SCRIPTS_DIR)/stop_service $(SERVICE_DIR)/
	mkdir -p $(SERVICE_DIR)/check_mk
	cp $(SCRIPTS_DIR)/data_api_service $(SERVICE_DIR)/check_mk/

test: shutdown startup
	@echo '+- Run nosetests from the data_api source directory, which will use the test data'
	KB_DEPLOY_URL=dir_nocache nosetests -c nose.cfg -c nose-local.cfg

startup:
	@echo '+- Start each of the API services'
	#nohup data_api_start_service.py --config deployment.cfg --service taxon --port 9101 & > taxonAPI.out
	#nohup data_api_start_service.py --config deployment.cfg --service assembly --port 9102 & > assemblyAPI.out        
	#nohup data_api_start_service.py --config deployment.cfg --service genome_annotation --port 9103 & > genome_annotationAPI.out
	data_api_start_service.py --config deployment.cfg --service taxon --port 9101  >taxon.out 2>&1 &
	data_api_start_service.py --config deployment.cfg --service assembly --port 9102 >assembly.out 2>&1 &
	data_api_start_service.py --config deployment.cfg --service genome_annotation --port 9103 >genome_annotation.out 2>&1 &

shutdown:
	@printf "+- Shutdown\n"
	ps auxw | grep "[d]ata_api_start_service" | cut -c17-23 | xargs kill
	@ sleep 2

clean:
	/bin/rm -f *.out *.pid
