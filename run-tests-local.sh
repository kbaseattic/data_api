#!/bin/sh
# check for test resource
if [ ! -e test_resources -o ! -d test_resources ]; then
    printf "Abort: Directory 'test_resources/' missing (or not a directory)\n"
    exit 1
fi
num_files=$(ls -l test_resources | wc -l)
if [ $num_files -eq 0 ]; then
    printf "Abort: Directory 'test_resources/' is empty\n"
    printf "You can check it out from git with this command:\n"
    printf "    git submodule update --init\n"
    exit 2
fi

# start services
data_api_start_service.py --config deployment.cfg --service taxon --port 9101  >taxon.out 2>&1 &
data_api_start_service.py --config deployment.cfg --service assembly --port 9102 >assembly.out 2>&1 &
data_api_start_service.py --config deployment.cfg --service genome_annotation --port 9103 >ga.out 2>&1 &

# parse flags from cmdline
verbose=0
coverage=0
module=""
while [ $# -gt 0 ]; do
    arg="$1"
    case $arg in
        -v) verbose=1
            shift
            ;;
        -c) coverage=1
            shift
            ;;
        *) module=$arg
            shift
            ;;
    esac
done

[ $verbose -eq 1 ] && tail -f taxon.out assembly.out ga.out &
if [ $coverage -eq 1 ]
then
    cmd="coverage run `which nosetests` -c nose.cfg -c nose-local.cfg $module"
else
    cmd="nosetests -c nose.cfg -c nose-local.cfg $module"
fi

sleep 3
printf "RUNNING: $cmd\n"
$cmd

sleep 3
ps auxw | grep [d]ata_api_start_service | cut -c12-21 | xargs kill

[ $coverage -eq 1 ] && coverage report
