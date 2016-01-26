"""
Examples for Genome Annotation API
"""
import os

from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI

# def get_proteins_for_gene(ref, gene, ws_url=None):
#     """Fetch all Proteins for a gene.
#
#     Args:
#       ws_url (str): a service address or a local directory
#          containing a downloaded version of the data created with the
#          ``dump_wsfile`` utility.
#     """
#     # Try to connect to remote service
#     obj = GenomeAnnotationAPI(token=os.environ.get('KB_AUTH_TOKEN'),
#                               ref=ref,
#                               services={'workspace_service_url': ws_url})
#     # Now the methods of the instance can be used
#     proteins = obj.get_proteins()
#     # TODO: filter by gene
#     return proteins
#
# def get_all_proteins_for_gene(ga=None, gene_id=None):
#     children_cds = ci_genome_annotation_api.get_child_features(ref=ga,
#                                                                from_type="gene",
#                                                                to_type="cds",
#                                                                feature_id_list=[
#                                                                    gene_id])
#     cds_id_list = [y.feature_id for y in childrens_cds[x] for x in children_cds]
#     proteins = genome_annotation_api.get_proteins_by_cds(ref=ga,
#                                                          cds_id_list=cds_id_list)
#
#     gene_to_proteins = dict()
#     for gene_id in children_cds:
#         gene_to_proteins[gene_id] = list()
#         for cds in children_cds[gene_id]:
#             gene_to_proteins[gene_id].extend(proteins[cds.feature_id])
#
#     return gene_to_proteins

def proteins_to_fasta(ws_url='https://ci.kbase.us/services/ws/'):
    """Write FASTA file from a genome reference.

    Args:
        ws_url: Workspace service URL

    Returns:
        Full path to output file
    """
    ref = "ReferenceGenomeAnnotations/kb|g.166819"
    # ref = "ReferenceGenomeAnnotations/kb|g.3899"
    genome_annotation = GenomeAnnotationAPI(
        token=os.environ.get('KB_AUTH_TOKEN'), services={
            'workspace_service_url': ws_url}, ref=ref)

    # Get all the proteins with the Data API
    proteins = genome_annotation.get_proteins()
    # Create an output file and write to it
    outfile = '/tmp/166819_prot.fasta'
    with open(outfile, 'w') as f:
        for fasta_line in get_fasta(proteins):
            f.write(fasta_line)

    return outfile

def get_aliases(data):
    string = ""
    for keys in data:
        string += str(keys) + " "
    return string

def get_fasta(data):
    i = 0
    for keys in data:
        i += 1
        if i > 3:
            break
        geneinfo = data[keys]
        aliases = get_aliases(geneinfo["protein_aliases"])
        function = geneinfo["protein_function"]
        sequence = geneinfo["protein_amino_acid_sequence"]
        yield '>{k} {f} {a}\n{s}\n'.format(k=keys, f=function, a=aliases,
                                           s=sequence)

