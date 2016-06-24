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
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI

#def main() :
if __name__ == '__main__':	
	#logger = script_utils.stderrlogger(__file__, level=logging.DEBUG)
	    
	token = os.environ.get("KB_AUTH_TOKEN")

	services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/",
            "handle_service_url": "https://ci.kbase.us/services/handle_service/"}

	try:
		print "starting"
		genome_ref = "7824/GCF_000005845.2_ASM584v2_genomic_GA"
		output_file_name = "test.gbk"
		GenomeAnnotation.downloadAsGBK(genome_ref, services, token, output_file_name, "./")
		print "done w upload"

		ga_api = GenomeAnnotationAPI(services, token=token, ref=genome_ref)

		feature_counts = ga_api.get_feature_type_counts()
		print feature_counts 

		gene = 0
		cds = 0
		mrna = 0
		with open(output_file_name, "r") as f:
			for line in f:
				if line.find("     gene            ") != -1:
					gene = gene+1
				elif line.find("     CDS             ") != -1:
					cds = cds+1
				elif line.find("     mRNA            ") != -1:
					mrna = mrna+1

		if 'mRNA' in feature_counts.keys() :
			if mrna != feature_counts['mRNA']:
				print "mrna count different "+str(mrna)+" vs "+str(feature_counts['mRNA'])
			else:
				print "mrna agree"
		if cds != feature_counts['CDS']:
			print "cds count different "+str(cds)+" vs "+str(feature_counts['CDS'])
		else:
			print "cds agree"
		if gene != feature_counts['gene']:
			print "gene count different "+str(gene)+" vs "+str(feature_counts['gene'])
		else:
			print "gene agree"

	except Exception, e:
	    #ogger.exception(e)
	    print "Exception"
	    raise
	    sys.exit(1)

	sys.exit(0)
