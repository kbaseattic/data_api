# Stdlib
import hashlib

# 3rd party
import Bio.Seq
import Bio.Alphabet

from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI

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
    taxon_object = TaxonAPI(services, token, taxon_ref)

    # fetch the genetic code for sequence translation
    genetic_code = taxon_object.get_genetic_code()

    # fetch the contigs for sequence extraction using locations
    contigs = assembly_object.get_contigs()

    features_locations_validator(features, contigs)

    feature_sequences = determine_sequences(features, contigs)
    print "Number of feature types: " + str(len(feature_sequences))
    feature_count = 0
    for type in feature_sequences:
        feature_count += len(feature_sequences[type])
    print "Number of features: " + str(feature_count)
    print "Number of CDS sequences : " + str(len(feature_sequences["CDS"]))

    protein_container, cds_warnings = create_protein_container(genome_annotation_name,
                                                               proteins,
                                                               feature_sequences["CDS"],
                                                               genetic_code)
    return [protein_container, cds_warnings]

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

    return (protein_container, cds_warnings)


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
