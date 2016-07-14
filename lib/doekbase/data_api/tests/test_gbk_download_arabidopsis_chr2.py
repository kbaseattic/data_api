#!/usr/bin/env python

# standard library imports
import sys
import os
import time
import argparse
import logging
import subprocess

# 3rd party imports
# None

# KBase imports
from doekbase.data_api.downloaders import GenomeAnnotation
#import GenomeAnnotation

if __name__ == '__main__':
    # logger = script_utils.stderrlogger(__file__, level=logging.DEBUG)

    token = os.environ.get("KB_AUTH_TOKEN")

    services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
                "shock_service_url": "https://ci.kbase.us/services/shock-api/",
                "handle_service_url": "https://ci.kbase.us/services/handle_service/"}

    try:

        genome_ref = "8020/3702_Ensembl_chr2"#"7824/GCF_000001735.3_TAIR10_genomic_GA"
        output_file_name = "3702_Ensembl_chr2.gbk"#"GCF_000001735.3_TAIR10_genomic_GA.gbk"

        start = time.time()
        print "starting"
        GenomeAnnotation.downloadAsGBK(genome_ref, services, token, output_file_name, "./")
        print "done"
        end = time.time()
        print str(end - start) + " s"

        start = time.time()
        GenomeAnnotation.testGBKDownload_vs_API(services, token, genome_ref, output_file_name)
        print "done testing"
        end = time.time()
        print str(end - start) + " s"

    except Exception, e:
        # ogger.exception(e)
        print "Exception"
        raise

    sys.exit(0)
