#!/usr/bin/env python

# standard library imports
import sys
import os
import time
import argparse
import logging
import subprocess
import pkgutil

# 3rd party imports
# None

# KBase imports
#sys.path.append("../downloaders")
#import GenomeAnnotation
from doekbase.data_api.downloaders import GenomeAnnotation

if __name__ == '__main__':

    print os.getcwd()
    print sys.path
    # logger = script_utils.stderrlogger(__file__, level=logging.DEBUG)

    token = os.environ.get("KB_AUTH_TOKEN")

    services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
                "shock_service_url": "https://ci.kbase.us/services/shock-api/",
                "handle_service_url": "https://ci.kbase.us/services/handle_service/"}

    # for importer, modname, ispkg in pkgutil.walk_packages(path=None, onerror=lambda x: None):
    #		print(modname)

    try:

        start = time.time()
        print "starting"
        genome_ref = "8431/12319_RefSeq"
        output_file_name = "12319_RefSeq.gbk"

        #print dir(GenomeAnnotation)

        GenomeAnnotation.downloadAsGBK(genome_ref, services, token, output_file_name, "./")
        print "done w upload"
        end = time.time()
        print str(end - start) + " s"

        #print sys.path
        start = time.time()
        GenomeAnnotation.testGBKDownload_vs_API(services, token, genome_ref, output_file_name)
        print "done testing"
        end = time.time()
        print str(end - start) + " s"


    except Exception, e:
        # logger.exception(e)
        print "Exception"
        raise

    sys.exit(0)
