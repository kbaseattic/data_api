#!/usr/bin/env python
"""
Run Taxon service.
"""

# stdlib
import argparse
import logging
import os
import sys
import ConfigParser
#import signal

# 3rd party
import lockfile
import lockfile.pidlockfile

# local
from doekbase.data_api.taxonomy.taxon.service import driver

# Logging
# TODO: add syslog support
g_log = logging.getLogger()
_hnd = logging.StreamHandler()
_hnd.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
g_log.addHandler(_hnd)

def main():

    service_name = 'taxon'
    global_stanza_name = 'data_api'
    service_stanza_name = service_name + '_api'
    # set defaults if nothing is set anywhere
    services = None
    pidfilename = service_name+"API.pid"
    service_port=9101

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="path to configuration file")
    parser.add_argument("--port", help="port to listen on (default " + str(service_port) + ")", type=int)
    # not sure how best to handle this, seems not to be used currently
    parser.add_argument("--kbase-url", help="prod, next, ci, localhost, dir", default="dir")
    parser.add_argument("--pidfile", help="path to pidfile to use")
    parser.add_argument('--verbose', '-v', dest='vb', action="count", default=0,
                        help="Print more verbose messages to standard error. "
                             "Repeatable. (default=ERROR)")

    args = parser.parse_args()

    # Set logging verbosity
    verbosity = (logging.ERROR, logging.INFO, logging.DEBUG)[min(args.vb, 2)]
    g_log.setLevel(verbosity)

    pidfilename = "TaxonAPI.pid"

    # Parse configuration
    config = ConfigParser.ConfigParser()
    if args.config:
        config.read(args.config)
    # get config
    if config.has_section(global_stanza_name):
        print "Reading global config from file " + args.config + " and stanza " + global_stanza_name
        ws = config.get(global_stanza_name,'workspace_service_url')
        shock = config.get(global_stanza_name,'shock_service_url')
        services = {'workspace_service_url': ws,
            'shock_service_url': shock}
    if config.has_section(service_stanza_name):
        print "Reading " + service_name + " config from file " + args.config + " and stanza " + service_stanza_name
        if config.has_option(service_stanza_name,'service-port'):
            service_port = config.getint(service_stanza_name,'service-port')
        if config.has_option(service_stanza_name,'pidfile'):
            pidfilename = config.get(service_stanza_name,'pidfile')

    # let command line override config file
    if args.pidfile:
        pidfilename = args.pidfile
    if args.port:
        service_port=args.port

    # test that the pidfile is not already locked with a running process
    pidfile = lockfile.pidlockfile.PIDLockFile(pidfilename, timeout=-1)
    try:
        pidfile.acquire()
    except lockfile.AlreadyLocked:
        try:
            #os.kill(pidfile.read_pid(), 0)
            pid = pidfile.read_pid()
            g_log.error("Server already running pid={:d}".format(pid))
            return 1
        except TypeError:
            # XXX: what does this mean?
            pidfile.break_lock()
    except lockfile.LockFailed:
        g_log.error("Unable to create process lock file '{}'".format(
            pidfilename))
        return 1

    pid = os.getpid()
    g_log.info('Creating PID lock file')
    try:
        # now that the pidfile is available, dump our pid for later
        with open(pidfilename, 'w') as outpidfile:
            outpidfile.write(str(pid) + "\n")

        #TODO set up signal handling for HUP, KILL
        #signal.signal(signal.SIGHUP, driver.reload_config())

        g_log.info("Starting service: port={:d}, PID={:d}".format(args.port,
                                                                  pid))
        try:
            print "starting service on port " + str(service_port)
            driver.start_service(services=services,port=service_port,host='')
        finally:
            pidfile.release()
    except lockfile.LockFailed:
        g_log.error("Unable to create process lock file '{}'".format(
            pidfilename))
        return 1

    g_log.info("Service stopped")

if __name__ == "__main__":
    sys.exit(main())
