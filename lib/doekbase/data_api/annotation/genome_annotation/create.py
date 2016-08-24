# Stdlib
import hashlib
import logging

# 3rd party
import Bio.Seq
import Bio.Alphabet

from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.workspace.client import Workspace

def create_genome_annotation(services=None,
                             token=None,
                             workspace_identifier=None,
                             genome_annotation_name=None,
                             features=None,
                             proteins=None,
                             assembly_ref=None,
                             taxon_ref=None,
                             annotation_properties=None):
    if not services:
        raise ValueError("Missing KBase services configuration!")
    elif not token:
        raise ValueError("Missing authentication token!")
    elif not workspace_identifier:
        raise ValueError("Missing workspace identifier!")
    elif not genome_annotation_name:
        raise ValueError("Missing GenomeAnnotation object name!")
    elif not features:
        raise ValueError("Missing feature data!")
    elif not assembly_ref:
        raise ValueError("Missing Assembly reference!")
    elif not taxon_ref:
        raise ValueError("Missing Taxon reference!")
    elif not annotation_properties:
        raise ValueError("Missing GenomeAnnotation properties!")

    assembly_object = AssemblyAPI(services,token,assembly_ref)

    if taxon_ref:
        taxon_object = TaxonAPI(services, token, taxon_ref)
    else:
        # set to the unknown taxon
        taxon_object = TaxonAPI(services, token, "ReferenceTaxons/unknown_taxon")

    # fetch the genetic code for sequence translation
    genetic_code = taxon_object.get_genetic_code()

    # fetch the contigs for sequence extraction using locations
    contigs = assembly_object.get_contigs()

    features_locations_validator(features, contigs)

    feature_sequences = determine_sequences(features, contigs)

    protein_container, cds_warnings, cds_protein_mappings = create_protein_container(genome_annotation_name,
                                                                                     proteins,
                                                                                     feature_sequences["CDS"],
                                                                                     genetic_code)

    feature_containers, feature_alias_lookup, warnings = create_feature_containers(genome_annotation_name,
                                                                                   features,
                                                                                   feature_sequences,
                                                                                   cds_protein_mappings,
                                                                                   cds_warnings,
                                                                                   workspace_identifier,
                                                                                   assembly_ref,
                                                                                   [])

    references = {}

    quality = create_quality_object(warnings)
    annotation = create_annotation_object(annotation_properties, references)

    if 0:
        ws = Workspace(services["workspace_service_url"], token=token)

        # save protein_container
        ws.save_objects({'id': workspace_identifier,
                         'objects': [{
                             "type": "GenomeAnnotations.ProteinContainer",
                             "data": protein_container,
                             "name": "",
                             "provenance": [],
                             "hidden": 1}
                         ]})
        # save quality object
        ws.save_objects({'id': workspace_identifier,
                         'objects': [{
                             "type": "GenomeAnnotations.FeatureContainer",
                             "data": feature_containers[t],
                             "name": "",
                             "provenance": [],
                             "hidden": 1
                            } for t in feature_containers]})
        # save quality object
        ws.save_objects({'id': workspace_identifier,
                         'objects': [{
                             "type": "GenomeAnnotations.AnnotationQuality",
                             "data": quality,
                             "name": "",
                             "provenance": [],
                             "hidden": 1}]})

        # save annotation object
        ws.save_objects({'id': workspace_identifier,
                         'objects': [{
                             "type": "GenomeAnnotations.GenomeAnnotation",
                             "data": annotation,
                             "name": "",
                             "provenance": [],
                             "hidden": 1}]})

        # save summary object

    return [protein_container, warnings, feature_containers, feature_alias_lookup]




def create_feature_containers(core_name=None, 
                              features=None, 
                              feature_sequences=None, 
                              cds_protein_mappings = None, 
                              cds_warnings = None,
                              workspace_identifier = None,
                              assembly_ref = None,
                              include_feature_types=None):
    if core_name is None:
        raise ValueError("No core_name supplied")

    if features is None:
        raise ValueError("No dictionary of features supplied")

    if feature_sequences is None:
        raise ValueError("No dictionary of feature sequences supplied")

    if cds_protein_mappings is None:
        raise ValueError("No dictionary of cds protein mappings supplied")

    if cds_warnings is None:
        cds_warnings = dict()

    if workspace_identifier is None:
        raise ValueError("No workspace indentifier was supplied")

    if assembly_ref is None:
        raise ValueError("No assembly reference was supplied")
        
    feature_types = list()
    #print "Feature sequences key : " + str(feature_sequences.keys())
    available_feature_types = feature_sequences.keys()
    if include_feature_types is not None and len(include_feature_types) > 0:
        #print "IN IF"
        #print "LENGTH OF INCLUDE FEATURES : " + str(len(include_feature_types))
        feature_types = include_feature_types
        for temp_feature_type in feature_types:
            if temp_feature_type not in available_feature_types:
                raise ValueError("Included Feature type {} is not the in the feature data provided".format(temp_feature_type))
    else:
        #print "IN ELSE"
        #Do all present feature types
        feature_types = available_feature_types

    #print "FEATURE TYPES : " + str(feature_types)

    feature_containers = dict() #dict with feature_type as top level key and then the feature container json as the value.
    feature_alias_lookup= dict() #Dict of feature alias lookups for the top level genome annotation object.
    warnings=list() #Warnings for the annotation quality object    
    protein_container_ref = "{}/{}_protein_container".format(workspace_identifier,core_name)

    for feature_id in features:
        feature = dict() #feature that is being built up this iteration
        input_feature = features[feature_id]
        feature_type = input_feature["feature_type"]
        if feature_type not in feature_types:
            #Do not process this feature 
            continue
        feature["type"] = feature_type
        container_object_name = "{}_{}".format(core_name,feature_type)
        if feature_type not in feature_containers:
            feature_containers[feature_type] = {
                "features" : dict(),
                "feature_container_id" : container_object_name,
                "type" : feature_type,
                "assembly_ref" : assembly_ref
            }

        feature["feature_id"] = feature_id
        if ("feature_function" in input_feature) and input_feature["feature_function"].strip() != "":
            feature["function"] = input_feature["feature_function"]
        if ("feature_aliases" in input_feature) and len(input_feature["feature_aliases"]) > 0 :
            feature["aliases"] = input_feature["feature_aliases"]
            #Process each alias and add them to the feature_alias_lookup
            for feature_alias in feature["aliases"]:
                if feature_alias not in feature_alias_lookup:
                    feature_alias_lookup[feature_alias] = list()
                feature_alias_lookup[feature_alias].append("{}/{}".format(workspace_identifier,container_object_name,feature_id))
        if feature_id not in feature_sequences[feature_type]:
            raise ValueError("There is no sequence {} in the feature_sequences dictionary".format(feature_id))
        else:
            seq = feature_sequences[feature_type][feature_id]
            feature["dna_sequence"] = seq
            feature["md5"] = hashlib.md5(seq.upper()).hexdigest()
            feature["dna_sequence_length"] = len(seq)
        #process the locations
        feature["locations"] = list()
        for location in input_feature["feature_locations"]:
            temp_list = [location["contig_id"], location["start"], location["strand"], location["length"]]
            feature["locations"].append(temp_list)
        if ("feature_inference" in input_feature) and input_feature["feature_inference"].strip() != "":
            feature["inference"] = input_feature["feature_inference"]
        if ("feature_notes" in input_feature) and input_feature["feature_notes"].strip() != "":
            feature["notes"] = input_feature["feature_notes"]
        #PUNTING ON PUBLICATIONS FOR NOW as uploader does not have feature level publications
        if (
            (("feature_warnings" in input_feature) and (len(input_feature["feature_warnings"]) > 0)) or 
            (feature_id in cds_warnings)):
            feature["quality_warnings"] = list()
            if (("feature_warnings" in input_feature) and (len(input_feature["feature_warnings"]) > 0)):
                for warning in input_feature["feature_warnings"]:
                    feature["quality_warnings"].append(warning)
                    warnings.append("{} : {}".format(feature_id, warning))
            if (feature_id in cds_warnings):
                warnings.append(cds_warnings[feature_id])
        if feature_type == "CDS":
            feature["CDS_properties"]={"codes_for_protein_ref":[protein_container_ref,cds_protein_mappings[feature_id]]}
        feature_containers[feature_type]["features"][feature_id]=feature
#        print "FEATURE : " + feature
#        exit()

    return (feature_containers, feature_alias_lookup, warnings)


def create_protein_container(core_name=None, proteins=None, cds_sequences=None, genetic_code=None):
    if core_name is None:
        raise ValueError("No core_name supplied")

    if proteins is None:
        raise ValueError("No dictionary of proteins supplied")

    if cds_sequences is None:
        raise ValueError("No dictionary of cds sequences supplied")

    if genetic_code is None:
        raise ValueError("No genetic code supplied")

    protein_container = {}
    protein_container["proteins"] = {}
    cds_warnings = {}
    protein_container_object_name = "{}_protein_container".format(core_name)
    protein_container['protein_container_id'] = protein_container_object_name
    protein_container['name'] = protein_container_object_name
    cds_protein_mappings = dict()
    for cds_id in proteins:
        input_protein = proteins[cds_id]
        protein = {"protein_id": input_protein["protein_id"]}

        if "protein_function" in input_protein:
            protein["function"] = input_protein["protein_function"]
        if "protein_aliases" in input_protein:
            protein["aliases"] = input_protein["protein_aliases"]

        # DO translation from the CDS Sequences input.
        if cds_id not in cds_sequences:
            raise KeyError("The cds sequences do not contain the CDS id {}".format(cds_id) +
                           "contained in the proteins dictionary.")

        cds_seq = Bio.Seq.Seq(cds_sequences[cds_id], Bio.Alphabet.generic_dna)
        translated_amino_acid_sequence = cds_seq.translate(table=genetic_code, to_stop=True)[0:].upper()

        if "protein_amino_acid_sequence" in input_protein:
            # check that sequence vs the translated sequence from the CDS_sequences dict
            protein["translation_derived"] = 0
            protein["amino_acid_sequence"] = input_protein["protein_amino_acid_sequence"].upper()
            # if not equal add a CDS warning
            if input_protein["protein_amino_acid_sequence"].upper() != translated_amino_acid_sequence:
                cds_warnings[cds_id] = "For {} ".format(cds_id) + \
                                       "the supplied amino acid sequence does not match " + \
                                       "the translated amino acid sequence"
        else:
            # use translated sequence
            protein["translation_derived"] = 1
            protein["amino_acid_sequence"] = translated_amino_acid_sequence

        protein["md5"] = hashlib.md5(protein["amino_acid_sequence"]).hexdigest()
        if protein["protein_id"] in protein_container["proteins"]:
            raise ValueError("Protein_id {} is duplicated, problem with input data".format(protein["protein_id"]))
        else:
            protein_container["proteins"][protein["protein_id"]] = protein
            cds_protein_mappings[cds_id]=protein["protein_id"]

    return (protein_container, cds_warnings, cds_protein_mappings)


def features_locations_validator(features=None, contigs=None):
    errors = list()
    if features is None or contigs is None:
        raise ValueError("Features or contigs was not supplied")
    for feature_id in features:
        feature = features[feature_id]
        if "feature_locations" not in feature:
            errors.append("Feature {} does not contain feature_locations".format(feature_id))
        else:
            for location in feature["feature_locations"]:
                contig_id = location["contig_id"]
                start = location["start"]
                strand = location["strand"]
                length = location["length"]

                if contig_id not in contigs:
                    errors.append(
                        "The contig ID {} in a feature location for {}".format(contig_id, feature_id) +
                        " is not found in the contigs for the assembly")
                else:
                    contig_length = contigs[contig_id]["length"]
                    if strand == "+":
                        if start + length - 1 > contig_length:
                            errors.append("The feature {}".format(feature_id) +
                                          " has feature location that is longer than the contig it is on.")
                        if start < 0:
                            errors.append("The feature {} has feature location that is below zero.".format(feature_id))
                    else:
                        if start > contig_length:
                            errors.append("The feature {}".format(feature_id) +
                                          " has feature location that is longer than the contig it is on.")
                        if start - length < 0:
                            errors.append("The feature {} has feature location that is below zero.".format(feature_id))
    if len(errors) > 0:
        raise Exception("Failed features location validation \n {} ".format(', '.join(map(str, errors))))
    else:
        return True

def determine_sequences(features=None, contigs=None):
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
                location_sequence = contigs[contig_id]["sequence"][start - 1:start + length - 1]
            else:
                location_sequence = contigs[contig_id]["sequence"][start - length:start]
                dna = Bio.Seq.Seq(location_sequence, Bio.Alphabet.IUPAC.ambiguous_dna)
                dna_reverse_complement = dna.reverse_complement()
                location_sequence = str(dna_reverse_complement)

            feature_sequence += location_sequence

        if feature_type not in feature_sequences:
            feature_sequences[feature_type] = {}
        feature_sequences[feature_type][feature_id]=feature_sequence
    return feature_sequences

def create_quality_object():
    pass

def create_annotation_object():
    pass

def create_summary_object():
    pass