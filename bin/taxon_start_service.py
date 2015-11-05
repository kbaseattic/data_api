#!/usr/bin/env python
"""
Run Taxon service.
"""

# stdlib
import argparse
import logging
import os
import sys
#import signal

# 3rd party
import lockfile
import lockfile.pidlockfile

# local
from doekbase.data_api.taxonomy.taxon.service import driver

# Logging
g_log = logging.getLogger()
_hnd = logging.StreamHandler()
_hnd.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
g_log.addHandler(_hnd)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="port to listen on", type=int, default=9101)
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
    if args.pidfile:
        pidfilename = args.pidfile

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
            driver.start_service(port=args.port)
        finally:
            pidfile.release()
    except lockfile.LockFailed:
        g_log.error("Unable to create process lock file '{}'".format(
            pidfilename))
        return 1

    g_log.info("Service stopped")

if __name__ == "__main__":
    sys.exit(main())
