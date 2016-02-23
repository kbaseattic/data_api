#!/bin/sh
data_api_start_service.py --config deployment.cfg --service taxon --port 9101  >taxon.out 2>&1 &
data_api_start_service.py --config deployment.cfg --service assembly --port 9102 >assembly.out 2>&1 &
data_api_start_service.py --config deployment.cfg --service genome_annotation --port 9103 >ga.out 2>&1 &

if [ "x$1" = "x-v" ]; then
    tail -f taxon.out assembly.out ga.out &
fi

sleep 3
nosetests -c nose.cfg -c nose-local.cfg

sleep 3
ps auxw | grep [d]ata_api_start_service | cut -c12-21 | xargs kill