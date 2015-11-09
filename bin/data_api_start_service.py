#!/usr/bin/env python

# stdlib
import argparse
import logging
import os
import sys
import ConfigParser

# 3rd party
import lockfile
import lockfile.pidlockfile

# local
from doekbase.data_api import cache

SERVICE_NAMES = ["object", "taxon", "assembly", "genomeannotation"]

# Logging
# TODO: add syslog support
logger = logging.getLogger()
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(log_handler)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="path to configuration file", required=True)
    parser.add_argument("--service",
                        help="service name to start, one of {}".format(SERVICE_NAMES),
                        required=True)
    parser.add_argument("--port", help="port to listen on", type=int)
    parser.add_argument("--kbase_url", help="prod, next, ci, localhost, dir", default="dir")
    parser.add_argument("--pidfile", help="path to pidfile to use")
    parser.add_argument('--verbose', '-v', dest='vb', action="count", default=1,
                        help="Print more verbose messages to standard error. "
                             "Repeatable. (default=INFO)")

    args = parser.parse_args()

    # Set logging verbosity
    verbosity = (logging.ERROR, logging.INFO, logging.DEBUG)[min(args.vb, 2)]
    logger.setLevel(verbosity)

    # Parse configuration
    config = ConfigParser.ConfigParser()
    if args.config:
        config.read(args.config)

    if args.service not in SERVICE_NAMES:
        logger.info("Unrecognized service name {}".format(args.service))
        return 1

    service_name = args.service
    global_stanza_name = 'data_api' + ".kbase." + args.kbase_url
    service_stanza_name = service_name + '_api'

    # set defaults if nothing is set anywhere
    services = None
    pidfilename = service_name + "API.pid"
    service_port = None
    redis_host = None
    redis_port = None

    # get config
    if config.has_section(global_stanza_name):
        logger.info("Reading global config:'{}', stanza:'{}'".format(args.config, global_stanza_name))
        ws = config.get(global_stanza_name,'workspace_service_url')
        shock = config.get(global_stanza_name,'shock_service_url')
        services = {'workspace_service_url': ws,
            'shock_service_url': shock}

        try:
            redis_host = config.get(global_stanza_name, 'redis_host')
            redis_port = config.get(global_stanza_name, 'redis_port')
        except ConfigParser.Error, e:
            redis_host = None
            redis_port = None

    if config.has_section(service_stanza_name):
        logger.info("Reading service:'{}', config:'{}', stanza:'{}'".format(service_name, args.config, service_stanza_name))
        if config.has_option(service_stanza_name,'service-port'):
            service_port = config.getint(service_stanza_name,'service-port')
        if config.has_option(service_stanza_name,'pidfile'):
            pidfilename = config.get(service_stanza_name,'pidfile')

    # let command line override config file
    if args.pidfile:
        pidfilename = args.pidfile
    if args.port:
        service_port = args.port

    if redis_host is not None and redis_port is not None:
        logger.info("Activating REDIS at host:{} port:{}".format(redis_host, redis_port))
        cache.ObjectCache.cache_class = cache.RedisCache
        cache.ObjectCache.cache_params = {'redis_host': redis_host, 'redis_port': redis_port}


    # test that the pidfile is not already locked with a running process
    pidfile = lockfile.pidlockfile.PIDLockFile(pidfilename, timeout=-1)
    try:
        pidfile.acquire()
    except lockfile.AlreadyLocked:
        try:
            #os.kill(pidfile.read_pid(), 0)
            pid = pidfile.read_pid()
            logger.error("Server already running pid={:d}".format(pid))
            return 1
        except TypeError:
            # If we could not find a running process, release the lock
            pidfile.break_lock()
    except lockfile.LockFailed:
        logger.error("Unable to create process lock file '{}'".format(
            pidfilename))
        return 1

    pid = os.getpid()
    logger.info('Creating PID lock file')
    try:
        # now that the pidfile is available, dump our pid for later
        with open(pidfilename, 'w') as outpidfile:
            outpidfile.write(str(pid) + "\n")

        #TODO set up signal handling for HUP, KILL
        #signal.signal(signal.SIGHUP, driver.reload_config())

        logger.info("Starting service: port={}, PID={}".format(service_port, pid))
        try:
            if service_name == "taxon":
                from doekbase.data_api.taxonomy.taxon.service import driver
            elif service_name == "assembly":
                from doekbase.data_api.sequence.assembly.service import driver
            else:
                raise Exception("Service not activated: {}".format(service_name))

            driver.start_service(services=services,port=int(service_port),host='')
        finally:
            pidfile.release()
    except lockfile.LockFailed:
        logger.error("Unable to create process lock file '{}'".format(
            pidfilename))
        return 1

    logger.info("Service stopped")

if __name__ == "__main__":
    sys.exit(main())
