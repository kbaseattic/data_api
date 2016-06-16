#!/usr/bin/env python

# standard library imports
import sys
import os
import argparse
import logging
import subprocess

# 3rd party imports
# None

# KBase imports
from doekbase.data_api.downloaders import GenomeAnnotation


def main() :
	#logger = script_utils.stderrlogger(__file__, level=logging.DEBUG)
	    
	token = os.environ.get("KB_AUTH_TOKEN")

	services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/",
            "handle_service_url": "https://ci.kbase.us/services/handle_service/"}

	try:
		print "starting"
	    downloadAsGBK("", services, token)
	    print "done"
	except Exception, e:
	    logger.exception(e)
	    sys.exit(1)

	sys.exit(0)