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


logger = script_utils.stderrlogger(__file__, level=logging.DEBUG)
    
    try:
        downloadAsGBK()
    except Exception, e:
        logger.exception(e)
        sys.exit(1)
    
    sys.exit(0)