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

if __name__ == '__main__':
    # logger = script_utils.stderrlogger(__file__, level=logging.DEBUG)

    token = os.environ.get("KB_AUTH_TOKEN")

    services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
                "shock_service_url": "https://ci.kbase.us/services/shock-api/",
                "handle_service_url": "https://ci.kbase.us/services/handle_service/"}

    try:

        genome_ref = "7824/GCF_000005845.2_ASM584v2_genomic_GA"
        output_file_name = "test.gbk"
        
        print "starting"
        GenomeAnnotation.downloadAsGBK("7824/GCF_000001735.3_TAIR10_genomic_GA", services, token, "test.gbk", "./")
        print "done"

        GenomeAnnotation.testGBKDownload_vs_API(services, token, genome_ref, output_file_name)
        print "done testing"

    except Exception, e:
        # ogger.exception(e)
        print "Exception"
        raise

    sys.exit(0)
