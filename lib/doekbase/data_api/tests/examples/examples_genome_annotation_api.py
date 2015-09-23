

def get_all_proteins_for_gene(ga=None, gene_id=None):
    children_cds = ci_genome_annotation_api.get_child_features(ref=ga, from_type="gene", to_type="cds", feature_id_list=[gene_id])
    cds_id_list = [y.feature_id for y in childrens_cds[x] for x in children_cds]
    proteins = genome_annotation_api.get_proteins_by_cds(ref=ga, cds_id_list=cds_id_list)
    
    gene_to_proteins = dict()
    for gene_id in children_cds:
        gene_to_proteins[gene_id] = list()
        for cds in children_cds[gene_id]:
            gene_to_proteins[gene_id].extend(proteins[cds.feature_id])
    
    return gene_to_proteins
