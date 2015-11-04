#!/bin/bash
script_dir=$(dirname "$(readlink -f "$0")")
export KB_DEPLOYMENT_CONFIG=$script_dir/../deploy.cfg

for api in taxon
do
    python $script_dir/../bin/${api}_start_service.py
done
