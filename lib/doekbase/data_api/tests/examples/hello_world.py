from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI

# Set up to connect to KBase services
auth_token = ""  # empty token is OK for public data
services = {'workspace_service_url': 'http://ci.kbase.us/services/ws/'}

if __name__ == '__main__':

    #########
    # Taxon #
    #########

    # Connect to the Taxon API
    object_id = '993/616059/2'  # format -> workspace/object/version
    obj = TaxonAPI(ref=object_id, services=services, token=auth_token)
    # Retrieve some information from it
    name = obj.get_scientific_name()
    # Tell the world
    print("Hello, World! Taxon {} is called {}".format(object_id, name))

    ############
    # Assembly #
    ############

    # Connect to the Assembly API
    object_id = '1013/92/2'  # format -> workspace/object/version
    obj = AssemblyAPI(ref=object_id, services=services, token=auth_token)
    # Retrieve some information from it
    info = obj.get_stats()
    # Tell the world
    info['oid'] = object_id
    print("Hello, World! Assembly {oid} has the following statistics:\n"
          "  GC content  : {gc_content}\n"
          "  DNA size    : {dna_size}\n"
          "  Num. contigs: {num_contigs}".format(**info))
