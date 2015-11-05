#!/usr/bin/env python

# stdlib
import argparse
import os
import sys
#import signal

# 3rd party
import lockfile
import lockfile.pidlockfile

# local
from doekbase.data_api.taxonomy.taxon.service import driver

# TODO add logging and syslog support
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="port to listen on", type=int, default=9101)
    parser.add_argument("--kbase-url", help="prod, next, ci, localhost, dir", default="dir")
    parser.add_argument("--pidfile", help="path to pidfile to use")
    args = parser.parse_args()

    pidfilename = "TaxonAPI.pid"
    if args.pidfile:
        pidfilename = args.pidfile

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
            driver.start_service(port=args.port,host='')
        finally:
            pidfile.release()
    except lockfile.LockFailed:
        print "Unable to create lock file for pid!"
        sys.exit(1)


if __name__ == "__main__":
    main()
