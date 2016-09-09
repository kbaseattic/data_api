# Stdlib
import hashlib
import re

# 3rd party
import Bio.Seq
import Bio.Alphabet

# local
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
                             annotation_properties=None,
                             provenance=None):
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

    assembly = AssemblyAPI(services, token, assembly_ref)

    if not taxon_ref:
        # set to the unknown taxon
        taxon_ref = "ReferenceTaxons/unknown_taxon"

    taxon = TaxonAPI(services, token, taxon_ref)
    # fetch the genetic code for sequence translation
    genetic_code = taxon.get_genetic_code()
    # fetch the scientific name, add the taxon and assembly references
    annotation_properties["display_sc_name"] = taxon.get_scientific_name()

    references = {
        "protein_container": "{}/{}_protein_container".format(workspace_identifier,
                                                              genome_annotation_name),
        "annotation_quality": "{}/{}_annotation_quality".format(workspace_identifier,
                                                                genome_annotation_name),
        "annotation": "{}/{}".format(workspace_identifier, genome_annotation_name),
        "assembly": assembly_ref,
        "taxon": taxon_ref,
        "feature_container": {}
    }

    feature_types = set([features[f].get("feature_type", None) for f in features])
    for t in feature_types:
        sanitized_typename = re.sub("\W+","",t)
        references["feature_container"][t] = "{}/{}_feature_container_{}".format(workspace_identifier,
                                                                                 genome_annotation_name,
                                                                                 sanitized_typename)

    # fetch the contigs for sequence extraction using locations
    contigs = assembly.get_contigs()

    features_locations_validator(features, contigs)
    feature_sequences = determine_sequences(features, contigs)

    protein_container, cds_warnings, cds_protein_mappings = create_protein_container(genome_annotation_name,
                                                                                     proteins,
                                                                                     feature_sequences["CDS"],
                                                                                     genetic_code)
    feature_containers, \
    feature_alias_lookup, \
    warnings, \
    feature_counts, \
    alias_source_counts = create_feature_containers(genome_annotation_name,
                                                    features,
                                                    feature_sequences,
                                                    cds_protein_mappings,
                                                    cds_warnings,
                                                    references)
    annotation_quality = create_annotation_quality(genome_annotation_name,
                                                   warnings,
                                                   feature_counts)
    annotation = create_annotation_object(genome_annotation_name,
                                          feature_counts,
                                          feature_alias_lookup,
                                          alias_source_counts,
                                          annotation_properties,
                                          references)

    try:
        ws = Workspace(services["workspace_service_url"], token=token)

        proteins_save = {
            "type": "KBaseGenomeAnnotations.ProteinContainer",
            "data": protein_container,
            "name": references["protein_container"].split("/")[1],
            "provenance": [],
            "hidden": 1
        }

        features_save = [
            {
                "type": "KBaseGenomeAnnotations.FeatureContainer",
                "data": feature_containers[t],
                "name": references["feature_container"][t].split("/")[1],
                "provenance": [],
                "hidden": 1
            } for t in feature_containers]

        quality_save = {
            "type": "KBaseGenomeAnnotations.AnnotationQuality",
            "data": annotation_quality,
            "name": references["annotation_quality"].split("/")[1],
            "provenance": [],
            "hidden": 1
        }

        annotation_save = {
            "type": "KBaseGenomeAnnotations.GenomeAnnotation",
            "data": annotation,
            "name": genome_annotation_name,
            "provenance": [],
            "hidden": 0
        }

        ws.save_objects({'id': workspace_identifier,
                         'objects': [proteins_save, quality_save]})
        ws.save_objects({'id': workspace_identifier,
                         'objects': features_save})
        ws.save_objects({'id': workspace_identifier,
                         'objects': [annotation_save]})
    except Exception, e:
        raise

    return "{}/{}".format(workspace_identifier, genome_annotation_name)


def create_feature_containers(genome_annotation_name=None,
                              features=None, 
                              feature_sequences=None, 
                              cds_protein_mappings=None,
                              cds_warnings=None,
                              references=None):
    if genome_annotation_name is None:
        raise ValueError("No genome_annotation_name supplied")

    if features is None:
        raise ValueError("No dictionary of features supplied")

    if feature_sequences is None:
        raise ValueError("No dictionary of feature sequences supplied")

    if cds_protein_mappings is None:
        raise ValueError("No dictionary of cds protein mappings supplied")

    if cds_warnings is None:
        cds_warnings = {}

    if references is None:
        raise ValueError("Missing object reference strings")

    feature_containers = {}
    feature_alias_lookup = {}
    alias_source_counts_map = {}
    all_warnings = []
    feature_counts = {}
    protein_container_ref = references["protein_container"]

    for feature_id in features:
        type = features[feature_id]["feature_type"]
        locations = features[feature_id]["feature_locations"]
        function = features[feature_id].get("feature_function", None)
        aliases = features[feature_id].get("feature_aliases", None)
        inference = features[feature_id].get("feature_inference", None)
        notes = features[feature_id].get("feature_notes", None)
        warnings = features[feature_id].get("feature_warnings", [])

        if feature_id not in feature_sequences[type]:
            raise ValueError("There is no sequence {} in the feature_sequences dictionary".format(feature_id))

        feature = {}

        feature["type"] = type
        feature["feature_id"] = feature_id

        if type == "CDS":
            feature["CDS_properties"] = {
                "codes_for_protein_ref": [protein_container_ref, cds_protein_mappings[feature_id]]
            }

        container_object_name = references["feature_container"][type].split("/")[1]

        if type not in feature_containers:
            feature_containers[type] = {
                "features": {},
                "feature_container_id": container_object_name,
                "type": type,
                "assembly_ref": references["assembly"]
            }
            feature_counts[type] = 0

        feature_counts[type] += 1

        feature["locations"] = [
            [location["contig_id"], location["start"], location["strand"], location["length"]]
            for location in locations]

        seq = feature_sequences[type][feature_id]
        feature["dna_sequence"] = seq
        feature["md5"] = hashlib.md5(seq.upper()).hexdigest()
        feature["dna_sequence_length"] = len(seq)

        if function and len(function.strip()) > 0:
            feature["function"] = function

        if inference and len(inference.strip()) > 0:
            feature["inference"] = inference

        if notes and len(notes.strip()) > 0:
            feature["notes"] = notes

        if aliases and len(aliases) > 0:
            feature["aliases"] = aliases

            for feature_alias in aliases:
                if feature_alias not in feature_alias_lookup:
                    feature_alias_lookup[feature_alias] = []

                feature_alias_lookup[feature_alias].append(
                    (references["feature_container"][type], feature_id))

                for alias_source in aliases[feature_alias]:
                    if alias_source not in alias_source_counts_map:
                        alias_source_counts_map[alias_source] = 0
                    alias_source_counts_map[alias_source] += 1

        # TODO - PUNTING ON PUBLICATIONS FOR NOW as uploader does not have feature level publications

        feature["quality_warnings"] = warnings
        all_warnings.extend(["{} : {}".format(feature_id, w) for w in warnings])

        if feature_id in cds_warnings:
            all_warnings.extend(cds_warnings[feature_id])

        feature_containers[type]["features"][feature_id] = feature

    return (feature_containers, feature_alias_lookup, all_warnings, feature_counts, alias_source_counts_map)


def create_protein_container(genome_annotation_name=None, proteins=None, cds_sequences=None, genetic_code=None):
    if genome_annotation_name is None:
        raise ValueError("No genome_annotation_name supplied")

    if proteins is None:
        raise ValueError("No dictionary of proteins supplied")

    if cds_sequences is None:
        raise ValueError("No dictionary of cds sequences supplied")

    if genetic_code is None:
        raise ValueError("No genetic code supplied")

    protein_container = {}
    protein_container["proteins"] = {}
    cds_warnings = {}
    protein_container_object_name = "{}_protein_container".format(genome_annotation_name)
    protein_container['protein_container_id'] = protein_container_object_name
    protein_container['name'] = protein_container_object_name
    cds_protein_mappings = {}

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

        translated_amino_acid_sequence = Bio.Seq.translate(cds_sequences[cds_id],
                                                           table=genetic_code,
                                                           to_stop=True)

        if "protein_amino_acid_sequence" in input_protein:
            # check that sequence vs the translated sequence from the CDS_sequences dict
            protein["translation_derived"] = 0
            protein["amino_acid_sequence"] = input_protein["protein_amino_acid_sequence"].upper()
            # if not equal add a CDS warning
            if protein["amino_acid_sequence"] != translated_amino_acid_sequence:
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
            cds_protein_mappings[cds_id] = protein["protein_id"]

    return (protein_container, cds_warnings, cds_protein_mappings)


def features_locations_validator(features=None, contigs=None):
    errors = []
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
    feature_sequences = {}
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


def create_annotation_quality(genome_annotation_name=None, warnings=None, feature_counts=None):
    if not genome_annotation_name:
        raise ValueError("No genome_annotation_name supplied")

    if not warnings:
        warnings = []

    if not feature_counts:
        raise ValueError("Missing feature_counts")

    annotation_quality_object = {
        "metadata_completeness": 0,
        "metadata_completeness_warnings": [],
        "data_quality": 0,
        "data_quality_warnings": warnings,
        "feature_types_present": len(feature_counts),
        "evidence_supported": 0
    }

    return annotation_quality_object


def create_annotation_object(genome_annotation_name=None,
                             feature_counts=None,
                             feature_alias_lookup=None,
                             alias_source_counts=None,
                             annotation_properties=None,
                             references=None,
                             reference_data=False):
    genome_annotation = {
        "feature_container_references": {
            feature_type: references["feature_container"][feature_type]
            for feature_type in feature_counts},
        "protein_container_ref": references["protein_container"],
        "annotation_quality_ref": references["annotation_quality"],
        "feature_lookup": feature_alias_lookup,
        "counts_map": feature_counts,
        "alias_source_counts_map": alias_source_counts,
        "genome_annotation_id": genome_annotation_name,
        "assembly_ref": references["assembly"],
        "taxon_ref": references["taxon"]
    }

    if reference_data:
        genome_annotation["reference_annotation"] = 1
    else:
        genome_annotation["reference_annotation"] = 0

    for k in annotation_properties:
        genome_annotation[k] = annotation_properties[k]

    return genome_annotation