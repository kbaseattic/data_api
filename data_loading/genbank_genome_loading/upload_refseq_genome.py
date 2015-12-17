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
import datetime
from string import digits

# 3rd party imports
import simplejson

# KBase imports
import biokbase.Transform.script_utils as script_utils
import TextFileDecoder
import biokbase.workspace.client 

def make_scientific_names_lookup(taxon_names_file=None):
   #key scientific name, value is taxon object name (taxid_taxon)
    scientific_names_lookup = dict() 
 
    if os.path.isfile(taxon_names_file): 
        print "Found taxon_names_File" 
        name_f = open(taxon_names_file, 'r') 
        for name_line in name_f: 
            temp_list = re.split(r'\t*\|\t*', name_line) 
#            scientific_names_lookup[temp_list[1]] = "%s_taxon" % (str(temp_list[0])) 
            scientific_names_lookup[temp_list[1]] = temp_list[0] 
        name_f.close() 
    return scientific_names_lookup


def insert_newlines(s, every): 
    lines = [] 
    for i in xrange(0, len(s), every): 
        lines.append(s[i:i+every]) 
    return "\n".join(lines)+"\n" 



# transformation method that can be called if this module is imported
# Note the logger has different levels it could be run.  
# See: https://docs.python.org/2/library/logging.html#logging-levels
#
# The default level is set to INFO which includes everything except DEBUG
def upload_genome(shock_service_url=None, 
              #handle_service_url=None, 
              #output_file_name=None, 
              #input_fasta_directory=None, 
              #working_directory=None, shock_id=None, handle_id=None, 
              input_file_name=None, 
              #fasta_reference_only=False,
              wsname=None,
              wsurl=None,
              genome_list_file=None,
              taxon_wsname=None,
              taxon_names_file=None,
              fasta_file_directory=None,
              core_genome_name=None,
              source=None,
              level=logging.INFO, logger=None):
    """
    Uploads CondensedGenomeAssembly
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


    scientific_names_lookup = make_scientific_names_lookup(taxon_names_file)

    ws_client = biokbase.workspace.client.Workspace(wsurl)
 
    workspace_object = ws_client.get_workspace_info({'workspace':wsname}) 

    workspace_id = workspace_object[0] 
    workspace_name = workspace_object[1] 
 
    taxon_ws_client = biokbase.workspace.client.Workspace(wsurl)
    taxon_workspace_object = ws_client.get_workspace_info({'workspace':taxon_wsname}) 

    taxon_workspace_id = taxon_workspace_object[0] 
    taxon_workspace_name = taxon_workspace_object[1] 
 
    #NEED TO FIND THE TAXON OBJECT
    #NEED TO GET ORGANISM NAME AND TAX ID FROM FILE
#    input_file_name = input_file_name[0]

    print "INPUT FILE NAME :" + input_file_name + ":"


    if os.path.isfile(input_file_name):
        print "Found Genbank_File" 
        genbank_file_handle = open(input_file_name, 'r')
        genbank_file = genbank_file_handle.read()
        genbank_file_handle.close()
        genbank_files = genbank_file.split("//\n")
#        print genbank_files[6]
#        sys.exit(0)
    else:
        print "NO GENBANK FILE"
        sys.exit(1)

    temp = genbank_files[-1]
    if temp.replace(" ", "") == "":
        del genbank_files[-1]
    
    print "Number of contigs : " + str(len(genbank_files))
   
    organism_dict = dict() 
    if len(genbank_files) < 1 :
        print "Error no genbank record found in the input file"
        sys.exit(1)
    else:
        record_lines = genbank_files[0].split("\n")
        for record_line in record_lines:
            if record_line.startswith("  ORGANISM  "):
                organism = record_line[12:]
                print "Organism Line :" + record_line + ":"
                print "Organism :" + organism + ":"
                organism_dict[organism] = 1
                break

    tax_id = 0;
    if organism in scientific_names_lookup: 
        tax_id = scientific_names_lookup[organism]
        taxon_object_name = "%s_taxon" % (str(tax_id)) 
    else: 
        genomes_without_taxon_refs.append(organism)
        taxon_object_name = "unknown_taxon"
        genome_annotation['notes'] = "Unable to find taxon for this organism : %s ." % (organism ) 
    try: 
        taxon_info = ws_client.get_object_info([{"wsid": str(taxon_workspace_id), "name": taxon_object_name}],0) 
        taxon_id = "%s/%s/%s" % (taxon_info[0][6], taxon_info[0][0], taxon_info[0][4]) 
        print "Found name : " + taxon_object_name + " id: " + taxon_id
    except Exception, e: 
        print str(e) 
        print "The taxon " + taxon_object_name + " from workspace " + str(taxon_workspace_id) + " does not exist."

    
    #CORE OBJECT NAME WILL BE EITHER PASSED IN GENERATED (TaxID_Source)
    #Fasta file name format is taxID_source_timestamp
    time_string = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H_%M_%S'))
    if core_genome_name is None:
        if source is None:
            source_name = "unknown_source"
        else:
            source_name = source
        if tax_id == 0:
            core_genome_name = "%s_%s" % (source_name,time_string) 
            fasta_file_name = "unknown_%s_%s.fa" % (source_name,time_string) 
        else:
            core_genome_name = "%s_%s" % (str(tax_id),source_name) 
            fasta_file_name = "%s_%s.fa" % (core_genome_name,time_string) 

    print "Core Genome Name :"+ core_genome_name + ":"
    print "FASTA FILE Name :"+ fasta_file_name + ":"

    now_date = datetime.datetime.now()
        
    #Parse LOCUS line from each file and grab that meta data (also establish order of the contigs)
    locus_name_order = list() #for knowing order of the genbank files/contigs
    genbank_metadata_objects = dict() #the data structure for holding the top level metadata information of each genbank file

    genbank_division_set = {'PRI','ROD','MAM','VRT','INV','PLN','BCT','VRL','PHG','SYN','UNA','EST','PAT','STS','GSS','HTG','HTC','ENV'}

    #Make the Fasta file for the sequences to be written to
    if fasta_file_directory is not None:
        fasta_file_name = "%s/%s" % (fasta_file_directory,fasta_file_name)
    fasta_file_handle = open(fasta_file_name, 'w')
    
    min_date = None
    max_date = None
    genbank_time_string = None
    genome_publication_list = list()
    genome_comment = ''

    for genbank_file in genbank_files:
        annotation_part, sequence_part = genbank_file.rsplit("ORIGIN",1)
        metadata_part, features_part = annotation_part.rsplit("FEATURES             Location/Qualifiers",1) 

        metadata_lines = metadata_part.split("\n")


        #METADATA PARSING PORTION
        for metadata_line in metadata_lines: 
            if metadata_line.startswith("ACCESSION   "): 
                temp = metadata_line[12:]
                accession = temp.split(' ', 1)[0]
                break

        #LOCUS line parsing
        locus_line_info = metadata_lines[0].split()
        genbank_metadata_objects[accession] = dict()
        locus_name_order.append(accession)
        genbank_metadata_objects[accession]["number_of_basepairs"] = locus_line_info[2]
        date_text = None
        if locus_line_info[4] != 'DNA':
            print "Error the record with the Locus Name of %s is not valid as the moecule type of %s , is not 'DNA'" % (locus_info_line[1],locus_info_line[4])
            fasta_file_handle.close()
            sys.exit(1)
        if locus_line_info[5] in genbank_division_set:
            genbank_metadata_objects[accession]["is_circular"] = "Unknown"
            date_text = locus_line_info[6]
        elif locus_line_info[6] in genbank_division_set:
            date_text = locus_line_info[7]
            if locus_line_info[5] == "circular":
                genbank_metadata_objects[accession]["is_circular"] = "True"
            elif locus_line_info[5] == "linear":
                genbank_metadata_objects[accession]["is_circular"] = "False"
            else:
                genbank_metadata_objects[accession]["is_circular"] = "Unknown"
        else:
            date_text = locus_line_info[5]

        try:
            record_time = datetime.datetime.strptime(date_text, '%d-%b-%Y')
            if min_date == None:
                min_date = record_time
            elif record_time < min_date:
                min_date = record_time
            if max_date == None:
                max_date = record_time
            elif record_time > max_date:
                max_date = record_time

        except ValueError:
            raise ValueError("Incorrect date format, should be 'DD-MON-YYYY'")
            fasta_file_handle.close()
            sys.exit(1)

        genbank_metadata_objects[accession]["external_source_origination_date"] = date_text

        num_metadata_lines = len(metadata_lines)
        metadata_line_counter = 0

        for metadata_line in metadata_lines:
            if metadata_line.startswith("DEFINITION  "):
                definition = metadata_line[12:]
                definition_loop_counter = 1
                if ((metadata_line_counter + definition_loop_counter)<= num_metadata_lines):
                    next_line = metadata_lines[metadata_line_counter + definition_loop_counter]
                    while (next_line.startswith("            ")) and ((metadata_line_counter + definition_loop_counter)<= num_metadata_lines) :
                        definition = "%s %s" % (definition,next_line[12:])
                        defintion_loop_counter += 1
                        if ((metadata_line_counter + definition_loop_counter)<= num_metadata_lines):
                            next_line = metadata_lines[metadata_line_counter + definition_loop_counter]
                        else:
                            break
                genbank_metadata_objects[accession]["definition"] = definition 
            elif metadata_line.startswith("  ORGANISM  "): 
                organism = metadata_line[12:] 
                if organism not in organism_dict:
                    raise ValueError("There is more than one organism represented in these Genbank files, they do not represent single genome.  First record's organism is %s , but %s was also found" % (str(organism_dict.keys()),organism)) 
                    fasta_file_handle.close() 
                    sys.exit(1) 
            elif metadata_line.startswith("COMMENT     "):
                comment = metadata_line[12:] 
                comment_loop_counter = 1 
                if ((metadata_line_counter + comment_loop_counter)<= num_metadata_lines):
                    next_line = metadata_lines[metadata_line_counter + comment_loop_counter] 
                    while (next_line.startswith("            ")) : 
                        comment = "%s %s" % (comment,next_line[12:]) 
                        comment_loop_counter += 1 
                        if ((metadata_line_counter + comment_loop_counter)<= num_metadata_lines):
                            next_line = metadata_lines[metadata_line_counter + comment_loop_counter]
                        else:
                            break
                genome_comment = "%s<%s :: %s> " % (genome_comment,accession,comment)
            elif metadata_line.startswith("REFERENCE   "):
                #PUBLICATION SECTION (long)
                authors = ''
                title = ''
                journal = ''
                pubmed = ''
                consortium = ''

                reference_loop_counter = 1
                if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines): 
                    next_line = metadata_lines[metadata_line_counter + reference_loop_counter] 
                # while (next_line and re.match(r'\s', next_line) and not nextline[0].isalpha()):
                while (next_line and re.match(r'\s', next_line)):
                    if next_line.startswith("  AUTHORS   "):
                        authors = next_line[12:] 
                        reference_loop_counter += 1
                        if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines):
                            next_line = metadata_lines[metadata_line_counter + reference_loop_counter] 
                        else:
                            break
                        while (next_line.startswith("            ")) :     
                            authors = "%s %s" % (authors,next_line[12:]) 
                            reference_loop_counter += 1
                            if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines): 
                                next_line = metadata_lines[metadata_line_counter + reference_loop_counter] 
                            else: 
                                break 
                    elif next_line.startswith("  TITLE     "):
                        title = next_line[12:]
                        reference_loop_counter += 1
                        if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines):
                            next_line = metadata_lines[metadata_line_counter + reference_loop_counter]
                        else:
                            break
                        while (next_line.startswith("            ")) :
                            title = "%s %s" % (title,next_line[12:])
                            reference_loop_counter += 1
                            if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines):
                                next_line = metadata_lines[metadata_line_counter + reference_loop_counter]
                            else:
                                break
                    elif next_line.startswith("  JOURNAL   "):
                        journal = next_line[12:]
                        reference_loop_counter += 1
                        if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines):
                            next_line = metadata_lines[metadata_line_counter + reference_loop_counter]
                        else:
                            break
                        while (next_line.startswith("            ")) :
                            journal = "%s %s" % (journal,next_line[12:])
                            reference_loop_counter += 1
                            if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines):
                                next_line = metadata_lines[metadata_line_counter + reference_loop_counter]
                            else:
                                break
                    elif next_line.startswith("   PUBMED   "): 
                        pubmed = next_line[12:] 
                        reference_loop_counter += 1
                        if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines):
                            next_line = metadata_lines[metadata_line_counter + reference_loop_counter]
                        else:
                            break
                        while (next_line.startswith("            ")) : 
                            pubmed = "%s %s" % (journal,next_line[12:]) 
                            reference_loop_counter += 1
                            if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines): 
                                next_line = metadata_lines[metadata_line_counter + reference_loop_counter] 
                            else: 
                                break 
                    elif next_line.startswith("  CONSRTM   "):
                        consortium = next_line[12:]
                        reference_loop_counter += 1
                        if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines): 
                            next_line = metadata_lines[metadata_line_counter + reference_loop_counter]
                        else:
                            break 
                        while (next_line.startswith("            ")) : 
                            consortium = "%s %s" % (journal,next_line[12:]) 
                            reference_loop_counter += 1
                            if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines):
                                next_line = metadata_lines[metadata_line_counter + reference_loop_counter]
                            else:
                                break
                    else:
                        if ((metadata_line_counter + reference_loop_counter)<= num_metadata_lines):
                            next_line = metadata_lines[metadata_line_counter + reference_loop_counter]
                        else:
                            break
                #Done grabbing reference lines, time to build the reference object.
#                authors = '' 
#                title = '' 
#                journal = '' 
#                pubmed = '' 
#                consortium = '' 

                pubmed_link = ''
                publication_source = ''
                publication_date = ''
                if pubmed != '':
                    publication_source = "PubMed"
                elif consortium != '':
                    publication_source = consortium
                try:
                    pubmed = int(pubmed)
                except ValueError:
                    pubmed = 0
                if pubmed != 0:
                    pubmed_link = "http://www.ncbi.nlm.nih.gov/pubmed/%s" % str(pubmed)
                if journal != '':
                    potential_date_regex = r'(?<=\().+?(?=\))'
                    potential_dates = re.findall(potential_date_regex, journal)

                    
                    for potential_date in reversed(potential_dates):                        
                        try:
                            record_time = datetime.datetime.strptime(potential_date, '%d-%b-%Y')
                            if now_date > record_time:
                                publication_date = potential_date
                                break
                        except ValueError:
                            try:
                                record_time = datetime.datetime.strptime(potential_date, '%b-%Y')
                                if now_date > record_time:
                                    publication_date = potential_date
                                    break       
                            except ValueError:
                                record_time = datetime.datetime.strptime(potential_date, '%Y')
                                if now_date > record_time:
                                    publication_date = potential_date
                                    break
                publication = [pubmed,publication_source,title,pubmed_link,publication_date,authors,journal]
                genome_publication_list.append(publication)
                #END OF PUBLICATION SECTION

            metadata_line_counter += 1


        sequence_part = sequence_part.translate(None, digits)
        sequence_part = re.sub('\s+','',sequence_part)
        sequence_part = sequence_part.replace("","?")

#        print "The len of sequence part is: " + str(len(sequence_part))
#        print "The number from the record: " + genbank_metadata_objects[accession]["number_of_basepairs"]        
#        print "First 100 of sequence part : " + sequence_part[0:100] 

        fasta_file_handle.write(">{}\n".format(accession))
        #write 80 nucleotides per line
        fasta_file_handle.write(insert_newlines(sequence_part,80))

        
        
    fasta_file_handle.close()
    if min_date == max_date:
        genbank_time_string = min_date.strftime('%d-%b-%Y').upper()
    else:
        genbank_time_string = "%s to %s" %(min_date.strftime('%d-%b-%Y').upper(), max_date.strftime('%d-%b-%Y').upper())

    print "PUBLICATIONS :" + str(genome_publication_list)

    print "GENOME COMMENTS : " + genome_comment


    sys.exit(1)

        
#    print "FASTA FILE NAME : " + fasta_file_name
#    print "genbank_metadata_objects:" + str(genbank_metadata_objects)
#    print "locus_name_order:" + str(locus_name_order)

#    print "Before exit"
#   sys.exit(0)

    logger.info("Starting conversion of FASTA to Assemblies")
    token = os.environ.get('KB_AUTH_TOKEN')
        
    logger.info("Building Assembly Object.")

#    temp_genome_id = genome_id
#    temp_genome_id.replace("|","\|")
#    input_file_name = "%s/%s.fasta" % (input_fasta_directory,temp_genome_id) 
#    if not os.path.isfile(input_file_name):
#        raise Exception("The input file name {0} is not a file!".format(input_file_name))        

#        if not os.path.isdir(args.working_directory):
#            raise Exception("The working directory {0} is not a valid directory!".format(working_directory))        

#        logger.debug(fasta_reference_only)



    input_file_handle = TextFileDecoder.open_textdecoder(fasta_file_name, 'ISO-8859-1')    
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
                if genbank_metadata_objects[fasta_key]["definition"] is not None:
                    contig_dict["description"] = genbank_metadata_objects[fasta_key]["definition"]
                contig_md5 = hashlib.md5(total_sequence.upper()).hexdigest() 
                contig_dict["md5"] = contig_md5 
                contig_set_md5_list.append(contig_md5)
                contig_dict["is_circular"] = genbank_metadata_objects[fasta_key]["is_circular"] 
                contig_dict["start_position"] = sequence_start
                contig_dict["num_bytes"] = sequence_stop - sequence_start


#                print "Sequence Start: " + str(sequence_start) + "Fasta: " + fasta_key
#                print "Sequence Stop: " + str(sequence_stop) + "Fasta: " + fasta_key
                fasta_dict[fasta_key] = contig_dict
               
                # get set up for next fasta sequence
                sequence_list = []
                sequence_exists = False
                
#               sequence_start = input_file_handle.tell()               
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
        if genbank_metadata_objects[fasta_key]["definition"] is not None:
            contig_dict["description"] = genbank_metadata_objects[fasta_key]["definition"]
        contig_md5 = hashlib.md5(total_sequence.upper()).hexdigest()
        contig_dict["md5"]= contig_md5
        contig_set_md5_list.append(contig_md5)
        contig_dict["is_circular"] = genbank_metadata_objects[fasta_key]["is_circular"] 
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
    contig_set_dict["assembly_id"] = "%s_assembly" % (core_genome_name)
    contig_set_dict["name"] = "%s_assembly" % (core_genome_name)
    contig_set_dict["external_source"] = source_name
    contig_set_dict["external_source_id"] = os.path.basename(input_file_name) 
#    contig_set_dict["external_source_origination_date"] = str(os.stat(input_file_name).st_ctime)
    contig_set_dict["external_source_origination_date"] = genbank_time_string
    contig_set_dict["contigs"] = fasta_dict
    contig_set_dict["dna_size"] = total_length
    contig_set_dict["gc_content"] = float(gc_length)/float(total_length)
    print "Fasta dict Keys :"+",".join(fasta_dict.keys())+":" 
    contig_set_dict["num_contigs"] = len(fasta_dict.keys())
    contig_set_dict["type"] = "Unknown"
    contig_set_dict["notes"] = "Note MD5s are generated from uppercasing the sequences" 
    contig_set_dict["taxon_ref"] = taxon_id


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
            assembly_info =  ws_client.save_objects({"workspace": workspace_name,"objects":[ 
                {"type":"KBaseGenomesCondensedPrototypeV2.Assembly", 
                 "data":contig_set_dict, 
                 "name": "%s_assembly" % (core_genome_name), 
                 "provenance":assembly_provenance}]}) 
            assembly_not_saved = False 
        except biokbase.workspace.client.ServerError as err: 
            print "ASSEMBLY SAVE FAILED ON genome " + str(core_genome_name) + " ERROR: " + err 
            raise 
        except: 
            print "ASSEMBLY SAVE FAILED ON genome " + str(core_genome_name) + " GENERAL_EXCEPTION: " + str(sys.exc_info()[0]) 
            raise 
    
    logger.info("Conversion completed.")


# called only if script is run from command line
if __name__ == "__main__":
    script_details = script_utils.parse_docs(upload_genome.__doc__)    

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
    parser.add_argument('--input_file_name', 
                        help="genbank file", 
                        nargs='?', required=True)
#    parser.add_argument('--taxon_names_file', nargs='?', help='file with scientific name to taxon id mapping information in it.', required=True)
    parser.add_argument('--wsname', nargs='?', help='workspace name to populate', required=True)
    parser.add_argument('--taxon_wsname', nargs='?', help='workspace name with taxon in it, assumes the same wsurl', required=True)
    parser.add_argument('--taxon_names_file', nargs='?', help='file with scientific name to taxon id mapping information in it.', required=True)
    parser.add_argument('--wsurl', action='store', type=str, nargs='?', required=True) 

    parser.add_argument('--core_genome_name', 
                        help="genbank file", 
                        nargs='?', required=False) 
    parser.add_argument('--fasta_file_directory', 
                        help="fasta_dile_directory", 
                        nargs='?', required=False) 
    parser.add_argument('--source', 
                        help="data source : examples Refseq, Genbank, Pythozyme, Gramene, etc", 
                        nargs='?', required=True) 


#    parser.add_argument('--genome_list_file', action='store', type=str, nargs='?', required=True) 

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
    
        upload_genome(shock_service_url = args.shock_service_url, 
#                  handle_service_url = args.handle_service_url, 
#                  output_file_name = args.output_file_name, 
                      input_file_name = args.input_file_name, 
#                  working_directory = args.working_directory, 
#                  shock_id = args.shock_id, 
#                  handle_id = args.handle_id,
#                  input_mapping = args.input_mapping,
                      wsname = args.wsname,
                      wsurl = args.wsurl,
                      taxon_wsname = args.taxon_wsname,
                      taxon_names_file = args.taxon_names_file,
                      core_genome_name = args.core_genome_name,
                      source = args.source,
#                      genome_list_file = args.genome_list_file,
                      logger = logger)
    except Exception, e:
        logger.exception(e)
        sys.exit(1)
    
    sys.exit(0)


