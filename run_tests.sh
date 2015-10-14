#!/bin/bash
#
# This is a developer tool intended for running the test suite with the
# correct arguments. It includes starting/stopping the caching with Redis
#
# Author: Dan Gunter <dkgunter@lbl.gov>

# Nose

NOSE=nosetests
NOSE_OPTS="--logging-filter=doekbase --with-timer"

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
    export KB_REDIS_HOST=localhost
}

function restart_redis () {
    stop_redis
    start_redis
}

# Misc

function show_help () {
    printf "usage: $0 [OPTIONS] MODE [ARGS...]\n"
    printf "OPTIONS:\n"
    printf "   -n     don't stop/restart Redis"
    printf "MODE:\n"
    printf "  ci      run against workspace in contin. integration\n"
    printf "  local   run against local workspace data objects\n"
    printf "\n"
    printf "  remaining arguments are passed to the nosetests command.\n"
}

function inst_lib () {
    printf "* installing Python library..\n"
    python setup.py install >/dev/null
    printf "  done"
}

# Main

# process options
CONTROL_REDIS=y
TRAVIS_MODE=n
case "$1" in
    "-n") 
        CONTROL_REDIS=n
        shift
        ;;
    "-T")
        TRAVIS_MODE=y
        shift
        ;;
esac

if [ $TRAVIS_MODE = n ]; then
    # process mode
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
fi

if [ $TRAVIS_MODE = y ]
then
    printf "==============================================\n"
    printf "  running tests with Redis caching\n"
    printf "==============================================\n"
    start_redis
    export KB_REDIS_HOST=localhost
    run_nose_local  --ws-url=test_resources/data --wsfile-msgpack
    sleep 1
    stop_redis
else
    # prepare
    [ $CONTROL_REDIS = y ] && restart_redis
    inst_lib

    # run
    printf "\n\nRUNNING TESTS\n\n"

    run_nose_$mode "$*"

    printf "\n\n"
    sleep 1

    # cleanup
    [ $CONTROL_REDIS = y ] && stop_redis
fi

exit 0
