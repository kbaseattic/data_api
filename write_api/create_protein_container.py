"""                                                                                                                                                                 
SaveGenomeAnnotationSummary.                                                                                                                                        
""" 
__author__ = 'Jason Baumohl <jkbaumohl@lbl.gov>' 
__date__ = '6/29/16' 
 
# Stdlib                                                                                                                                                            
import hashlib 
import itertools 
import logging 
import os 
import string 
 
import  doekbase.workspace.client 
import json 
import doekbase.data_api 
from doekbase.data_api.sequence.assembly.api import AssemblyAPI, AssemblyClientAPI 
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI, TaxonClientAPI 
 
import time 
import os 

from Bio.Seq import Seq
from Bio.Alphabet import IUPAC, generic_dna 


def create_protein_container(core_name=None, proteins=None, cds_sequences=None, genetic_code=None):
    if core_name is None:
        raise ValueError("No core_name supplied")    

    if proteins is None:
        raise ValueError("No dictionary of proteins supplied")

    if cds_sequences is None:
        raise ValueError("No dictionary of cds sequences supplied")

    if genetic_code is None:
        raise ValueError("No genetic code supplied")

    protein_container = dict()
    protein_container["proteins"] = dict()
    cds_warnings=dict()
    protein_container_object_name = "%s_protein_container" % (core_name)
    protein_container['protein_container_id'] = protein_container_object_name 
    protein_container['name'] = protein_container_object_name
    for cds_id in proteins:
        protein = dict()
        input_protein=proteins[cds_id]
        if "protein_function" in input_protein:
            protein["function"]= input_protein["protein_function"]
        if "protein_aliases" in input_protein:
            protein["aliases"]= input_protein["protein_aliases"]
        protein["protein_id"] = input_protein["protein_id"]
        #DO translation from the CDS Sequences input.
        if cds_id not in cds_sequences:
            raise KeyError("The cds sequences do not contain the CDS id %s contained in the proteins dict." % (cds_id))
        cds_seq = Seq(cds_sequences[cds_id], generic_dna)
        temp_amino_acid_sequence = cds_seq.translate(table=genetic_code, to_stop=True)
        translated_amino_acid_sequence = str(temp_amino_acid_sequence[0:].upper())

        if "protein_amino_acid_sequence" in input_protein:
            #check that sequence vs the translated sequence from the CDS_sequences dict
            protein["translation_derived"] = 0
            protein["amino_acid_sequence"] = input_protein["protein_amino_acid_sequence"].upper()
            #if not equal add a CDS warning
            if input_protein["protein_amino_acid_sequence"].upper() != translated_amino_acid_sequence:
                cds_warnings[cds_id] = "For %s the supplied amino acid sequence does not match the translated amino acid sequence" % (cds_id)
        else:
            #use translated sequence
            protein["translation_derived"] = 1
            protein["amino_acid_sequence"] = translated_amino_acid_sequence


        protein["md5"] = hashlib.md5(protein["amino_acid_sequence"]).hexdigest()
        if protein["protein_id"] in protein_container["proteins"]:
            raise ValueError("Protein_id %s is duplicated, problem with input data" % (protein["protein_id"]))
        else:
            protein_container["proteins"][protein["protein_id"]]=protein

    return (protein_container,cds_warnings)

def features_locations_validator(features=None,contigs=None):
    errors = list()
    if features is None or contigs is None:
        raise ValueError("Features or contigs was not supplied")
    for feature_id in features:
        feature = features[feature_id]
        if "feature_locations" not in feature:
            errors.append("Feature %s does not contain feature_locations" % (feature_id))
        else:
            for location in feature["feature_locations"]:
                contig_id = location["contig_id"]
                start = location["start"]
                strand = location["strand"]
                length = location["length"]
            if contig_id not in contigs:
                errors.append("The contig ID %s in a feature location for %s is not found in the contigs for the assembly" % (contig_id,feature_id))
            else:
                contig_length = contigs[contig_id]["length"]
                if strand == "+":
                    if start+length-1 > contig_length:
                        errors.append("The feature %s has feature location that is longer than the contig it is on." % (feature_id))
                    if start < 0:
                        errors.append("The feature %s has feature location that is below zero." % (feature_id))
                else:
                    if start > contig_length:
                        errors.append("The feature %s has feature location that is longer than the contig it is on." % (feature_id))
                    if start-length < 0:
                        errors.append("The feature %s has feature location that is below zero." % (feature_id))
    if len(errors) > 0:
        raise Exception("Failed features location validation \n %s " % (', '.join(map(str, errors))))
    else:
        return True
        


def determine_sequences(features=None,contigs=None):
    feature_sequences = dict() #key feature id, value is the feature sequence
    for feature_id in features: 
        feature = features[feature_id] 
        feature_sequence = ""
        feature_type = feature["feature_type"]
        for location in feature["feature_locations"]:
            contig_id = location["contig_id"]
            start = location["start"]
            strand = location["strand"] 
            length = location["length"]
            if strand == "+":
                location_sequence = contigs[contig_id]["sequence"][start-1:start+length-1]
            else:
                location_sequence = contigs[contig_id]["sequence"][start-length:start]
                my_dna = Seq(location_sequence, IUPAC.ambiguous_dna)
                my_dna = my_dna.reverse_complement()
                location_sequence = str(my_dna)
            feature_sequence += location_sequence
        if feature_type not in feature_sequences:
            feature_sequences[feature_type]=dict()
        feature_sequences[feature_type][feature_id]=feature_sequence
    return feature_sequences        

if __name__ == "__main__":
    file = "../lib/doekbase/data_api/annotation/genome_annotation/exchange_dir/8020_11_1.json"
    core_name = file.replace(".json","")        
    with open(file) as json_data:
        d = json.load(json_data)
        json_data.close()

    services = { 
        "workspace_service_url": "https://ci.kbase.us/services/ws/",
        "shock_service_url": "https://ci.kbase.us/services/shock-api/",
        "handle_service_url": "https://ci.kbase.us/services/handle_service/"
    } 
    
    ws_client = doekbase.workspace.client.Workspace(services["workspace_service_url"]) 
 
    assembly_ref = d["assembly_ref"]
    taxon_ref = d["taxon_ref"]

    print "TAXON : " + str(taxon_ref)

    assembly_object = AssemblyAPI(services = services,
                                  token=os.environ.get('KB_AUTH_TOKEN'),
                                  ref=assembly_ref)
    taxon_object = TaxonAPI(services = services,
                            token=os.environ.get('KB_AUTH_TOKEN'),
                            ref=taxon_ref)
 
    genetic_code = taxon_object.get_genetic_code()
    
    print "Genetic code is :" + str(genetic_code)

    contigs = assembly_object.get_contigs() 

#    print "CONTIGS : " + str(contigs.keys())
    if(features_locations_validator(features=d["features"],contigs=contigs)):
        feature_sequences = determine_sequences(features=d["features"],contigs=contigs)
        print "Number of feature types: " + str(len(feature_sequences))
        feature_count = 0
        for type in feature_sequences:
            feature_count += len(feature_sequences[type])
        print "Number of features: " + str(feature_count)

        print "Number of CDS sequences : " + str(len(feature_sequences["CDS"]))

        (protein_container_to_made,cds_warnings ) = create_protein_container(core_name="Test",
                                                                             proteins=d["proteins"],
                                                                             cds_sequences=feature_sequences["CDS"],
                                                                             genetic_code=genetic_code)

        print "Number of CDS warnings : " + str(len(cds_warnings))
        print str(cds_warnings)

    exit()

