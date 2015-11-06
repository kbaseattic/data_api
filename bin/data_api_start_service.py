#!/usr/bin/env python

# stdlib
import argparse
import os
import sys
import ConfigParser

# 3rd party
import lockfile
import lockfile.pidlockfile

# local
from doekbase.data_api import cache

SERVICE_NAMES = ["object", "taxon", "assembly", "genomeannotation"]

# TODO add logging and syslog support
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="path to configuration file", required=True)
    parser.add_argument("--service",
                        help="service name to start, one of {}".format(SERVICE_NAMES),
                        required=True)
    parser.add_argument("--port", help="port to listen on", type=int)
    parser.add_argument("--kbase_url", help="prod, next, ci, localhost, dir", default="dir")
    parser.add_argument("--pidfile", help="path to pidfile to use")
    args = parser.parse_args()

    config = ConfigParser.ConfigParser()

    if args.config:
        config.read(args.config)

    if args.service not in SERVICE_NAMES:
        print "Unrecognized service name {}".format(args.service)
        sys.exit(1)

    global_stanza_name = 'data_api' + ".kbase." + args.kbase_url
    service_stanza_name = args.service + '_api'
    # set defaults if nothing is set anywhere
    services = None
    pidfilename = args.service + "API.pid"
    service_port = None
    redis_host = None
    redis_port = None

    # get config
    if config.has_section(global_stanza_name):
        print "Reading global config from file " + args.config + " and stanza " + global_stanza_name
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
        print "Reading " + service_name + " config from file " + args.config + " and stanza " + service_stanza_name
        if config.has_option(service_stanza_name,'service-port'):
            service_port=config.getint(service_stanza_name,'service-port')
        if config.has_option(service_stanza_name,'pidfile'):
            pidfilename=config.get(service_stanza_name,'pidfile')

    # let command line override config file
    if args.pidfile:
        pidfilename = args.pidfile
    if args.port:
        service_port=args.port

    if redis_host is not None and redis_port is not None:
        print "Activating REDIS at host:{} port:{}".format(redis_host,redis_port)
        cache.ObjectCache.cache_class = cache.RedisCache
        cache.ObjectCache.cache_params = {'redis_host': redis_host, 'redis_port': redis_port}


    # test that the pidfile is not already locked with a running process
    pidfile = lockfile.pidlockfile.PIDLockFile(pidfilename, timeout=-1)
    try:
        pidfile.acquire()
    except lockfile.AlreadyLocked:
        try:
            os.kill(pidfile.read_pid(), 0)
            print "Process already running!"
            sys.exit(1)
        except TypeError:
            pidfile.break_lock()
    except lockfile.LockFailed:
        print "Unable to create lock file for pid!"
        sys.exit(1)

    try:
        # now that the pidfile is available, dump our pid for later
        with open(pidfilename, 'w') as outpidfile:
            outpidfile.write(str(os.getpid()) + "\n")

        #TODO set up signal handling for HUP, KILL
        #signal.signal(signal.SIGHUP, driver.reload_config())

        try:
            print "starting service on port " + str(service_port)

            if args.service == "taxon":
                from doekbase.data_api.taxonomy.taxon.service import driver
            elif args.service == "assembly":
                from doekbase.data_api.sequence.assembly.service import driver
            else:
                raise Exception("Service not activated: {}".format(args.service))

            driver.start_service(services=services,port=service_port,host='')
        finally:
            pidfile.release()
    except lockfile.LockFailed:
        print "Unable to create lock file for pid!"
        sys.exit(1)


if __name__ == "__main__":
    main()
