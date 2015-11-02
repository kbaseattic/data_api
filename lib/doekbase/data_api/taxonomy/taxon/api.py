"""
Data API for Taxon entities.  This API provides methods for traversing
taxonomic parent/child relationships, and accessing information such as
NCBI taxonomic id, scientific name, scientific lineage, etc.
"""

# Stdlib
import abc

# Third-party

# Local
from doekbase.data_api.core import ObjectAPI
from doekbase.data_api.util import get_logger

_log = get_logger(__file__)

_GENOME_TYPES = ['KBaseGenomes.Genome']
_TAXON_TYPES = ['KBaseGenomesCondensedPrototypeV2.Taxon']
TYPES = _GENOME_TYPES + _TAXON_TYPES


class TaxonInterface(object):
    """Represents a Taxonomic Unit, e.g., species.

    Built to support KBaseGenomesCondensedPrototypeV2.Taxon and
    KBaseGenomes.Genome.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_parent(self, ref_only=False):
        """Retrieve parent Taxon.

        Args:
          ref_only (bool): Return the reference instead of the full
                           TaxonAPI object.
        Returns:
          TaxonAPI, or str: Parent Taxon, either as an object or a
                    reference.

        Raises:
          AttributeError: If no Parent Taxon exists for this Taxon.
         """
        pass

    @abc.abstractmethod
    def get_children(self, ref_only=False):
        """Retrieve the children Taxon of this Taxon as TaxonAPI objects.
        If this is accessing a Genome object, returns None.

        Returns:
          list<TaxonAPI>
        """
        pass

    @abc.abstractmethod
    def get_genome_annotations(self, ref_only=False):
        """Retrieve the GenomeAnnotations that refer to this Taxon.
        If this is accessing a Genome object, returns None.

        Returns:
          list<GenomeAnnotationAPI>
        """
        pass

    @abc.abstractmethod
    def get_scientific_lineage(self):
        """Retrieve the scientific lineage of this Taxon.

        Returns:
          str

          e.g., "Top unit;Middle unit;Lowest unit" """
        pass

    @abc.abstractmethod
    def get_scientific_name(self):
        """Retrieve the scientific name of this Taxon.

        Returns:
          str

          e.g., Escherichia Coli K12 str. MG1655"""
        pass

    @abc.abstractmethod
    def get_taxonomic_id(self):
        """Retrieve the NCBI taxonomic id of this Taxon.
        The KBaseGenomes.Genome type's closest representative is source_id.

        Returns:
          int

        Raises:
          AttributeError: If the NCBI taxonomic id for this Taxon is not present."""
        pass

    @abc.abstractmethod
    def get_kingdom(self):
        """Retrieve the kingdom associated with this Taxonomic Unit.

        Returns:
          str"""
        pass

    @abc.abstractmethod
    def get_domain(self):
        """Retrieve the domain associated with this Taxonomic Unit.

        Returns:
          str"""
        pass

    @abc.abstractmethod
    def get_aliases(self):
        """Retrieve the aliases for this Taxonomic Unit.

        Returns:
          list<str>"""
        pass

    @abc.abstractmethod
    def get_genetic_code(self):
        """Retrieve the genetic code for this Taxonomic Unit.

        Returns:
          int"""
        pass


class _KBaseGenomes_Genome(ObjectAPI, TaxonInterface):
    def __init__(self, services, token, ref):
        super(_KBaseGenomes_Genome, self).__init__(services, token, ref)

        self.data = self.get_data_subset(["taxonomy", "scientific_name", "source_id", "domain", "genetic_code"])

    def get_parent(self, ref_only=False):
        raise AttributeError

    def get_children(self, ref_only=False):
        return list()

    def get_genome_annotations(self, ref_only=False):
        from doekbase.data_api.annotation.genome_annotation import GenomeAnnotationAPI
        return [GenomeAnnotationAPI(self.services, self._token, self.ref)]

    def get_scientific_lineage(self):
        return [x.strip() for x in self.data["taxonomy"].split(";")]

    def get_scientific_name(self):
        return self.data["scientific_name"]

    def get_taxonomic_id(self):
        try:
            return int(self.data["source_id"])
        except (KeyError, ValueError):
            raise AttributeError

    def get_kingdom(self):
        raise AttributeError

    def get_domain(self):
        return self.data["domain"]

    def get_aliases(self):
        return list()

    def get_genetic_code(self):
        return self.data["genetic_code"]


class _Prototype(ObjectAPI, TaxonInterface):
    def __init__(self, services, token, ref):
        super(_Prototype, self).__init__(services, token, ref)

        self.data = self.get_data()

    def get_parent(self, ref_only=False):
        try:
            parent_ref = self.data["parent_taxon_ref"]
        except KeyError:
            raise AttributeError

        if ref_only:
            return parent_ref
        else:
            return TaxonAPI(self.services, token=self._token, ref=parent_ref)

    def get_children(self, ref_only=False):
        referrers = self.get_referrers()
        children = list()

        if ref_only:
            for object_type in referrers:
                if object_type.split('-')[0] in _TAXON_TYPES:
                    children.extend(referrers[object_type])
        else:
            for object_type in referrers:
                if object_type.split('-')[0] in _TAXON_TYPES:
                    children.extend([TaxonAPI(self.services, token=self._token, ref=y) for y in referrers[object_type]])

        return children

    def get_genome_annotations(self, ref_only=False):
        import doekbase.data_api.annotation.genome_annotation

        referrers = self.get_referrers()
        annotations = list()

        if ref_only:
            for object_type in referrers:
                if object_type.split('-')[0] in doekbase.data_api.annotation.genome_annotation.TYPES:
                    annotations.extend(referrers[object_type])
        else:
            for object_type in referrers:
                if object_type.split('-')[0] in doekbase.data_api.annotation.genome_annotation.TYPES:
                    for x in referrers[object_type]:
                        annotations.append(doekbase.data_api.annotation.genome_annotation.GenomeAnnotationAPI(
                            self.services, self._token, ref=x))

        return annotations

    def get_scientific_lineage(self):
        return [x.strip() for x in self.data["scientific_lineage"].split(";")]

    def get_scientific_name(self):
        return self.data["scientific_name"]

    def get_taxonomic_id(self):
        return self.data["taxonomy_id"]

    def get_kingdom(self):
        if "kingdom" in self.data:
            return self.data["kingdom"]
        else:
            raise AttributeError

    def __str__(self):
        """Simple string representation, for debugging.
        """
        return 'Id: {}, Name: {}, Lineage: {}'.format(
            self.get_taxonomic_id(),
            self.get_scientific_name(),
            self.get_scientific_lineage()
        )

    def get_domain(self):
        return self.data["domain"]

    def get_aliases(self):
        if "aliases" in self.data:
            return self.data["aliases"]
        else:
            return list()

    def get_genetic_code(self):
        return self.data["genetic_code"]


class TaxonAPI(ObjectAPI, TaxonInterface):
    def __init__(self, services=None, token=None, ref=None):
        """
        Defines which types and type versions that are legal.
        """

        super(TaxonAPI, self).__init__(services, token, ref)

        is_genome_type = self._typestring.split('-')[0] in _GENOME_TYPES
        is_taxon_type = self._typestring.split('-')[0] in _TAXON_TYPES

        if not (is_genome_type or is_taxon_type):
            raise TypeError("Invalid type! Expected one of {0}, received {1}".format(TYPES, self._typestring))

        if is_taxon_type:
            self.proxy = _Prototype(services, token, ref)
        else:
            self.proxy = _KBaseGenomes_Genome(services, token, ref)

    def get_parent(self, ref_only=False):
        return self.proxy.get_parent(ref_only)

    def get_children(self, ref_only=False):
        return self.proxy.get_children(ref_only)

    def get_genome_annotations(self, ref_only=False):
        return self.proxy.get_genome_annotations(ref_only)

    def get_scientific_lineage(self):
        return self.proxy.get_scientific_lineage()

    def get_scientific_name(self):
        return self.proxy.get_scientific_name()

    def get_taxonomic_id(self):
        return self.proxy.get_taxonomic_id()

    def get_kingdom(self):
        return self.proxy.get_kingdom()

    def get_domain(self):
        return self.proxy.get_domain()

    def get_aliases(self):
        return self.proxy.get_aliases()

    def get_genetic_code(self):
        return self.proxy.get_genetic_code()

    def __str__(self):
        """Simple string representation, for debugging.
        """

        try:
            tax_id = self.get_taxonomic_id()
        except AttributeError:
            tax_id = None

        return '[{}] Id: {}, Name: {}, Lineage: {}'.format(
            type(self.proxy),
            tax_id,
            self.get_scientific_name(),
            self.get_scientific_lineage()
        )

class TaxonClientAPI(TaxonInterface):
    def __init__(self, host='localhost', port=9090, token=None, ref=None):
        from doekbase.data_api.taxonomy.taxon.service.interface import TaxonClientConnection

        #TODO add exception handling and better error messages here
        self.host = host
        self.port = port
        self.transport, self.client = TaxonClientConnection(host, port).get_client()
        self.ref = ref
        self._token = token


    def get_info(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_info(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_history(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_history(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_provenance(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_provenance(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_id(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_id(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_name(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_name(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_version(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_version(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_parent(self, ref_only=False):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            parent_ref = self.client.get_parent(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

        if ref_only:
            return parent_ref
        else:
            return TaxonClientAPI(self.host, self.port, self._token, parent_ref)

    def get_children(self, ref_only=False):
        if not self.transport.isOpen():
                self.transport.open()

        try:
            children_refs = self.client.get_children(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

        if ref_only:
            return children_refs
        else:
            children = list()
            for x in children_refs:
                children.append(TaxonClientAPI(self.host, self.port, self._token, x))

            return children

    def get_genome_annotations(self, ref_only=False):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_genome_annotations(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_scientific_lineage(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_scientific_lineage(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_scientific_name(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            yield self.client.get_scientific_name(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_taxonomic_id(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_taxonomic_id(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_kingdom(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_kingdom(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_domain(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_domain(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_aliases(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_aliases(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()

    def get_genetic_code(self):
        if not self.transport.isOpen():
            self.transport.open()

        try:
            return self.client.get_genetic_code(self._token, self.ref)
        except Exception, e:
            raise
        finally:
            self.transport.close()
