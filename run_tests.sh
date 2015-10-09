#!/bin/bash
#
# This is a developer tool intended for running the test suite with the
# correct arguments. It includes starting/stopping the caching with Redis
#
# Author: Dan Gunter <dkgunter@lbl.gov>

# Nose

NOSE=nosetests
NOSE_OPTS="--logging-filter=doekbase"

function run_nose_ci () {
    $NOSE $NOSE_OPTS \
    --ws-url="https://ci.kbase.us/services/ws/" \
    $1
}


function run_nose_local () {
    $NOSE $NOSE_OPTS \
    --ws-url="./test_resources/data" \
    --wsfile-msgpack \
    $1
}

# Redis

REDIS=redis-server
REDIS_CONFIG=redis.conf

function stop_redis () {
    printf "* stopping redis..\n"
    pid=$(ps auxw | grep "[r]edis" | cut -c12-22)
    if [ "$pid" != "" ]; then
        printf "  killing PID $pid\n"
        kill $pid
        # wait for server to exit
        while [ "$pid" != "" ]
        do
            sleep 1
            pid=$(ps auxw | grep "[r]edis" | cut -c12-22)
        done
        printf "  removing dump-file: dump.rdb\n"
        /bin/rm -f dump.rdb
    else
        printf "  no running server found\n"
    fi
    printf "  done\n"
}

function start_redis () {
    version=$($REDIS --version)
    printf "* starting redis (%s) ..\n" "$version"
    ${REDIS} ${REDIS_CONFIG} >/dev/null &
}

function restart_redis () {
    stop_redis
    start_redis
}

# Misc

function show_help () {
    printf "usage: $0 MODE ...\n"
    printf "  if MODE is 'ci', run against workspace in contin. integration\n"
    printf "  if MODE is 'local', run against local workspace data objects\n"
    printf "\n"
    printf "  remaining arguments are passed to the nosetests command.\n"
}

function inst_lib () {
    printf "* installing Python library..\n"
    python setup.py install >/dev/null
    printf "  done"
}

# Main

mode="$1"
shift

case $mode in
    ci)
        mode=ci
        ;;
    local)
        mode=local
        ;;
    *)
        show_help
        exit 1
        ;;
esac


# prepare
restart_redis
inst_lib

# run
printf "\n\nRUNNING TESTS\n\n"

run_nose_$mode "$*"

printf "\n\n"
sleep 1

# cleanup
stop_redis

exit 0