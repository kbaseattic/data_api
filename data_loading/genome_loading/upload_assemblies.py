#!/usr/bin/env python

# standard library imports
import os
import sys
import logging
import re
import hashlib
import time 
import traceback 
import os.path 


# 3rd party imports
import simplejson

# KBase imports
import doekbase.Transform.script_utils as script_utils
import TextFileDecoder
import doekbase.workspace.client

# transformation method that can be called if this module is imported
# Note the logger has different levels it could be run.  
# See: https://docs.python.org/2/library/logging.html#logging-levels
#
# The default level is set to INFO which includes everything except DEBUG
def transform(shock_service_url=None, 
              #handle_service_url=None, 
              #output_file_name=None, 
              input_fasta_directory=None, 
              #working_directory=None, shock_id=None, handle_id=None, 
              #input_mapping=None, fasta_reference_only=False,
              wsname=None,
              wsurl=None,
              genome_list_file=None,
#              taxon_wsname=None,
#              taxon_names_file=None,
              level=logging.INFO, logger=None):
    """
    Uploads KBaseGenomeAnnotations.Assembly
    Args:
        shock_service_url: A url for the KBase SHOCK service.
        input_fasta_directory: The directory where files will be read from.
        level: Logging level, defaults to logging.INFO.
        
    Returns:
        JSON file on disk that can be saved as a KBase workspace object.
    Authors:
        Jason Baumohl, Matt Henderson
    """

    if logger is None:
        logger = script_utils.stderrlogger(__file__)


    assembly_ws_client = doekbase.workspace.client.Workspace(wsurl)
 
    assembly_workspace_object = assembly_ws_client.get_workspace_info({'workspace':wsname}) 
 
#    taxon_ws_client = doekbase.workspace.client.Workspace(wsurl)
 
#    taxon_workspace_object = ws_client.get_workspace_info({'workspace':taxon_wsname}) 
 
    workspace_id = assembly_workspace_object[0] 
    workspace_name = assembly_workspace_object[1] 


#    #key scientific name, value is taxon object name (taxid_taxon)
#    scientific_names_lookup = dict()
#    taxon_names_file = taxon_names_file[0]

#    if os.path.isfile(taxon_names_file): 
#        print "Found taxon_names_File" 
#        name_f = open(taxon_names_file, 'r') 
#        counter = 0 
#        for name_line in name_f: 
#            temp_list = re.split(r'\t*\|\t*', name_line) 
#            if temp_list[3] == "scientific name": 
#                scientific_names_lookup[temp_list[1]] = "%s_taxon" % (str(temp_list[0]))
#        name_f.close()


    genomes_list = list()
#    genome_list_file = genome_list_file[0]
    if os.path.isfile(genome_list_file): 
        print "Found Genome_list_File" 
    genomes_f = open(genome_list_file, 'r') 
    for genome_line in genomes_f: 
        temp_list = re.split(r'\n*', genome_line)
        genomes_list.append(temp_list[0])
    genomes_f.close()

    logger.info("Starting conversion of FASTA to Assemblies")
    token = os.environ.get('KB_AUTH_TOKEN')
        
#    if input_mapping is None:
#        logger.info("Scanning for FASTA files.")
#        valid_extensions = [".fa",".fasta",".fna"]
#        files = os.listdir(input_directory)
#        fasta_files = [x for x in files if os.path.splitext(x)[-1] in valid_extensions]
#        assert len(fasta_files) != 0
#        logger.info("Found {0}".format(str(fasta_files)))
#        input_file_name = os.path.join(input_directory,files[0])
#        if len(fasta_files) > 1:
#            logger.warning("Not sure how to handle multiple FASTA files in this context. Using {0}".format(input_file_name))
#    else:
#        input_file_name = os.path.join(os.path.join(input_directory, "FASTA.DNA.Assembly"), simplejson.loads(input_mapping)["FASTA.DNA.Assembly"])
        
    for genome_id in genomes_list:

        logger.info("Building Object.")

        temp_genome_id = genome_id
        temp_genome_id.replace("|","\|")
        input_file_name = "%s/%s.fasta" % (input_fasta_directory,temp_genome_id) 
        if not os.path.isfile(input_file_name):
            raise Exception("The input file name {0} is not a file!".format(input_file_name))        

#        if not os.path.isdir(args.working_directory):
#            raise Exception("The working directory {0} is not a valid directory!".format(working_directory))        

#        logger.debug(fasta_reference_only)


        input_file_handle = TextFileDecoder.open_textdecoder(input_file_name, 'ISO-8859-1')
 #   input_file_handle = open(input_file_name, 'r')
    
        fasta_header = None
        sequence_list = []
        fasta_dict = dict()
        first_header_found = False
        contig_set_md5_list = []
        # Pattern for replacing white space
        pattern = re.compile(r'\s+')
        sequence_exists = False
    
        total_length = 0
        gc_length = 0
        #Note added X and x due to kb|g.1886.fasta
        valid_chars = "-AaCcGgTtUuWwSsMmKkRrYyBbDdHhVvNnXx"
        amino_acid_specific_characters = "PpLlIiFfQqEe" 

        sequence_start = 0
        sequence_stop = 0

        current_line = input_file_handle.readline()
#    for current_line in input_file_handle:
        while current_line != None and len(current_line) > 0:

#        print "CURRENT LINE: " + current_line
            if (current_line[0] == ">"):
                # found a header line
                # Wrap up previous fasta sequence
                if (not sequence_exists) and first_header_found:
                    logger.error("There is no sequence related to FASTA record : {0}".format(fasta_header))        
                    raise Exception("There is no sequence related to FASTA record : {0}".format(fasta_header))
                if not first_header_found:
                    first_header_found = True
                #                sequence_start = input_file_handle.tell()
                    sequence_start = 0
                else:
                    sequence_stop = input_file_handle.tell() - len(current_line)
                    # build up sequence and remove all white space
                    total_sequence = ''.join(sequence_list)
                    total_sequence = re.sub(pattern, '', total_sequence)
                    if not total_sequence :
                        logger.error("There is no sequence related to FASTA record : {0}".format(fasta_header)) 
                        raise Exception("There is no sequence related to FASTA record : {0}".format(fasta_header))
                    for character in total_sequence:
                        if character not in valid_chars:
                            if character in amino_acid_specific_characters:
                                raise Exception("This fasta file may have amino acids in it instead of the required nucleotides.")
                            raise Exception("This FASTA file has non nucleic acid characters : {0}".format(character))
                    length = len(total_sequence)
                    total_length = total_length + length
                    contig_gc_length = len(re.findall('G|g|C|c',total_sequence))
                    contig_dict = dict() 
                    contig_dict["gc_content"] = float(contig_gc_length)/float(length) 
                    gc_length = gc_length + contig_gc_length
                    fasta_key = fasta_header.strip()
                    contig_dict["contig_id"] = fasta_key 
                    contig_dict["length"] = length 
                    contig_dict["name"] = fasta_key 
                    contig_dict["description"] = "Note MD5 is generated from uppercasing the sequence" 
                    contig_md5 = hashlib.md5(total_sequence.upper()).hexdigest() 
                    contig_dict["md5"] = contig_md5 
                    contig_set_md5_list.append(contig_md5)
                    contig_dict["is_circular"] = "unknown"
                    contig_dict["start_position"] = sequence_start
                    contig_dict["num_bytes"] = sequence_stop - sequence_start


#                    print "Sequence Start: " + str(sequence_start) + "Fasta: " + fasta_key
#                    print "Sequence Stop: " + str(sequence_stop) + "Fasta: " + fasta_key
                    fasta_dict[fasta_key] = contig_dict
               
                    # get set up for next fasta sequence
                    sequence_list = []
                    sequence_exists = False
                
#                    sequence_start = input_file_handle.tell()               
                sequence_start = 0            

                fasta_header = current_line.replace('>','')
            else:
                if sequence_start == 0:
                    sequence_start = input_file_handle.tell() - len(current_line) 
                sequence_list.append(current_line)
                sequence_exists = True
            current_line = input_file_handle.readline()

        # wrap up last fasta sequence
        if (not sequence_exists) and first_header_found: 
            logger.error("There is no sequence related to FASTA record : {0}".format(fasta_header))        
            raise Exception("There is no sequence related to FASTA record : {0}".format(fasta_header)) 
        elif not first_header_found :
            logger.error("There are no contigs in this file") 
            raise Exception("There are no contigs in this file") 
        else: 
            sequence_stop = input_file_handle.tell()
            # build up sequence and remove all white space      
            total_sequence = ''.join(sequence_list)
            total_sequence = re.sub(pattern, '', total_sequence)
            if not total_sequence :
                logger.error("There is no sequence related to FASTA record : {0}".format(fasta_header)) 
                raise Exception("There is no sequence related to FASTA record : {0}".format(fasta_header)) 

            for character in total_sequence: 
                if character not in valid_chars: 
                    if character in amino_acid_specific_characters:
                        raise Exception("This fasta file may have amino acids in it instead of the required nucleotides.")
                    raise Exception("This FASTA file has non nucleic acid characters : {0}".format(character))

            length = len(total_sequence)
            total_length = total_length + length
            contig_gc_length = len(re.findall('G|g|C|c',total_sequence))
            contig_dict = dict()
            contig_dict["gc_content"] = float(contig_gc_length)/float(length) 
            gc_length = gc_length + contig_gc_length
            fasta_key = fasta_header.strip()
            contig_dict["contig_id"] = fasta_key 
            contig_dict["length"] = length
            contig_dict["name"] = fasta_key
            contig_dict["description"] = "Note MD5 is generated from uppercasing the sequence" 
            contig_md5 = hashlib.md5(total_sequence.upper()).hexdigest()
            contig_dict["md5"]= contig_md5
            contig_set_md5_list.append(contig_md5)
            contig_dict["is_circular"] = "unknown"
            contig_dict["start_position"] = sequence_start
            contig_dict["num_bytes"] = sequence_stop - sequence_start
        
            fasta_dict[fasta_key] = contig_dict 
        input_file_handle.close()

#        if output_file_name is None:
#            # default to input file name minus file extenstion adding "_contig_set" to the end
#            base = os.path.basename(input_file_name)
#            output_file_name = "{0}_contig_set.json".format(os.path.splitext(base)[0])
    
        contig_set_dict = dict()
        contig_set_dict["md5"] = hashlib.md5(",".join(sorted(contig_set_md5_list))).hexdigest()
        contig_set_dict["assembly_id"] = genome_id
        contig_set_dict["name"] = genome_id
        contig_set_dict["external_source"] = "KBase"
        contig_set_dict["external_source_id"] = os.path.basename(input_file_name) 
        contig_set_dict["external_source_origination_date"] = str(os.stat(input_file_name).st_ctime)
        contig_set_dict["contigs"] = fasta_dict
        contig_set_dict["dna_size"] = total_length
        contig_set_dict["gc_content"] = float(gc_length)/float(total_length)
        contig_set_dict["num_contigs"] = len(fasta_dict.keys())
        contig_set_dict["type"] = "Unknown"
        contig_set_dict["notes"] = "Unknown"

        shock_id = None
        if shock_id is None:
            shock_info = script_utils.upload_file_to_shock(logger, shock_service_url, input_file_name, token=token)
            shock_id = shock_info["id"]
    
        contig_set_dict["fasta_handle_ref"] = shock_id

        # For future development if the type is updated to the handle_reference instead of a shock_reference


        assembly_not_saved = True 
        assembly_provenance = [{"script": __file__, "script_ver": "0.1", "description": "Generated from fasta files generated from v5 of the CS."}]
        while assembly_not_saved: 
            try: 
                assembly_info =  assembly_ws_client.save_objects({"workspace": workspace_name,"objects":[ 
                            {"type":"KBaseGenomeAnnotations.Assembly", 
                             "data":contig_set_dict, 
                             "name": "%s_assembly" % (genome_id), 
                             "provenance":assembly_provenance}]}) 
                assembly_not_saved = False 
            except doekbase.workspace.client.ServerError as err:
                print "SAVE FAILED ON genome " + str(genome_id) + " ERROR: " + err 
                raise 
            except: 
                print "SAVE FAILED ON genome " + str(genome_id) + " GENERAL_EXCEPTION: " + str(sys.exc_info()[0]) 
                raise 
    
        logger.info("Conversion completed.")


# called only if script is run from command line
if __name__ == "__main__":
    script_details = script_utils.parse_docs(transform.__doc__)    

    import argparse

    parser = argparse.ArgumentParser(prog=__file__, 
                                     description=script_details["Description"],
                                     epilog=script_details["Authors"])
                                     
    parser.add_argument('--shock_service_url', 
                        help=script_details["Args"]["shock_service_url"],
                        action='store', type=str, nargs='?', required=True)
#    parser.add_argument('--handle_service_url', 
#                        help=script_details["Args"]["handle_service_url"], 
#                        action='store', type=str, nargs='?', default=None, required=False)
    parser.add_argument('--input_fasta_directory', 
                        help=script_details["Args"]["input_fasta_directory"], 
                        action='store', type=str, nargs='?', required=True)
    parser.add_argument('--wsname', nargs='?', help='workspace name to populate', required=True)
#    parser.add_argument('--taxon_wsname', nargs='?', help='workspace name with taxon in it, assumes the same wsurl', required=True)
#    parser.add_argument('--taxon_names_file', nargs='?', help='file with scientific name to taxon id mapping information in it.', required=True)
    parser.add_argument('--wsurl', action='store', type=str, nargs='?', required=True) 
    parser.add_argument('--genome_list_file', action='store', type=str, nargs='?', required=True) 

#    parser.add_argument('--working_directory', 
#                        help=script_details["Args"]["working_directory"], 
#                        action='store', type=str, nargs='?', required=True)
#    parser.add_argument('--output_file_name', 
#                        help=script_details["Args"]["output_file_name"],
#                        action='store', type=str, nargs='?', default=None, required=False)
#    parser.add_argument('--shock_id', 
#                        help=script_details["Args"]["shock_id"],
#                        action='store', type=str, nargs='?', default=None, required=False)
#    parser.add_argument('--handle_id', 
#                        help=script_details["Args"]["handle_id"], 
#                        action='store', type=str, nargs='?', default=None, required=False)

#    parser.add_argument('--input_mapping', 
#                        help=script_details["Args"]["input_mapping"], 
#                        action='store', type=unicode, nargs='?', default=None, required=False)

    args, unknown = parser.parse_known_args()

    logger = script_utils.stderrlogger(__file__)

    logger.debug(args)
    try:
    
        transform(shock_service_url = args.shock_service_url, 
#                  handle_service_url = args.handle_service_url, 
#                  output_file_name = args.output_file_name, 
                  input_fasta_directory = args.input_fasta_directory, 
#                  working_directory = args.working_directory, 
#                  shock_id = args.shock_id, 
#                  handle_id = args.handle_id,
#                  input_mapping = args.input_mapping,
                  wsname = args.wsname,
                  wsurl = args.wsurl,
#                  taxon_wsname = args.taxon_wsname,
#                  taxon_names_file = args.taxon_names_file,
                  genome_list_file = args.genome_list_file,
                  logger = logger)
    except Exception, e:
        logger.exception(e)
        sys.exit(1)
    
    sys.exit(0)


