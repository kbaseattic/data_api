"""
Objects for displaying the results in the IPython notebook.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/1/15'

from IPython.display import display
import pandas as pd
try:
    import qgrid
except ImportError:
    qgrid = None
from jinja2 import Template

_nbviewer = False
def nbviewer_mode(value=None):
    """Get/set the global nbviewer-friendly mode.
    This is currently used to tell qgrid where to get
    its JavaScript from (local or a CDN).
    """
    global _nbviewer
    if value is not None:
        _nbviewer = bool(value)
    return _nbviewer

class Table(pd.DataFrame):
    """Create a Table from the input data.
    This is a thin wrapper around the Pandas DataFrame object.
    """
    def _ipython_display(self):
        if qgrid:
            return qgrid.show_grid(self, remote_js=nbviewer_mode())
        else:
            return display(self)

class Contigs(Table):
    def __init__(self, contigs):
        """Create contigset from list of strings.

        Args:
          contigs: List of strings for contigs
        """
        Table.__init__(self, {'ids': contigs})

class TemplateMixin(object):
    template = ''
    def __init__(self):
        self._template = Template(self.template)

    def render(self, *args, **kwargs):
        return self._template.render(*args, **kwargs)

class Classification(TemplateMixin):
    """Taxonomic classification.

    Attributes:
      taxon (TaxonAPI): base taxon
      name (str): Scientific name
      children (list of TaxonAPI): List of TaxonAPI objects
      parents (list of Taxon
    """
    template = '''{% for name in classification %}
    <span style="margin-left: {{ loop.index0 * 10 }}px">
    <span style="font-size: 50%">&gt;</span>&nbsp;{{ name }}
    </span><br>{% endfor %}'''

    def __init__(self, obj):
        """Create from a taxon.

        Args:
          obj: TaxonAPI object or object with `get_taxon`.
        """
        TemplateMixin.__init__(self)
        self.taxon = obj.get_taxon() if hasattr(obj, 'get_taxon') else obj
        self.name = self.taxon.get_scientific_name()
        self.children = self.taxon.get_children() or []
        tx, self.parents = self.taxon, []
        while tx:
            tx = tx.get_parent()
            if tx:
                self.parents.insert(tx.get_scientific_name(), 0)
        self.classification = self.parents + [self.name] + [
            child.get_scientific_name() for child in self.children]

    def _repr_html_(self):
        return self.render(classification=self.classification)

class Organism(TemplateMixin):
    """Summary of an organism as per ENSEMBL page, from
    a TaxonAPI.

    Attributes:
      taxon (TaxonAPI): Taxon with info for organism
    """
    template = '''<b>Taxonomy ID</b>: {{taxon.get_taxonomic_id()}}<br>
        <b>Name</b>: {{taxon.get_scientific_name()}}<br>
        <b>Aliases</b>:<br>
        {% for a in taxon.get_aliases() %}
        &nbsp;&nbsp;{{ a }}<br>
        {% endfor %}
        <b>Classification</b>:<br>''' + \
        Classification.template

    def __init__(self, obj):
        """Create from an API object.

        Args:
          obj: TaxonAPI object or object with `get_taxon`.
        """
        TemplateMixin.__init__(self)
        self.taxon = obj.get_taxon() if hasattr(obj, 'get_taxon') else obj

    def _repr_html_(self):
        if self.taxon is None:
            return None
        classf = Classification(self.taxon).classification
        return self.render(classification=classf, taxon=self.taxon)

class AssemblyInfo(TemplateMixin):
    """Get information about assembly.

    Attributes:
      stats (dict): Statistics from `AssemblyAPI.get_stats()`
    """
    template = '''<b>GC content</b>: {{gc_content}}<br>
    <b>Total DNA sequence length</b>:{{dna_size}}<br>
    <b>Number of contigs</b>:{{num_contigs}}'''

    def __init__(self, obj):
        """Create assembly info.

        Args:
          obj: AssemblyAPI or object with `get_assembly` method.
        """
        TemplateMixin.__init__(self)
        if hasattr(obj, 'get_assembly'):
            self.assembly = obj.get_assembly()
        else:
            self.assembly = obj
        self.stats = self.assembly.get_stats()

    def _repr_html_(self):
        return self.render(self.stats)

class FeatureStats(Table):
    """Feature information for genomes
    """
    def __init__(self, ga):
        """Create from a genome.

        Args:
          ga: GenomeAnnotationAPI object
        """
        data = []
        for feature in ga.get_feature_types(): # all feature types
            count = 0
            # get lists of positions for each feature_id
            feature_id_lists = ga.get_feature_ids_by_type([feature])
            for fi, values in feature_id_lists.items():
                count += len(values)
            data.append((feature, count))
        Table.__init__(self, data, columns=('feature_type', 'count'))

###################################

# def __rb_parsing(self)was found
#     in a Rhodobacter genome.
#         NODE_48_length_21448_cov_4.91263_ID_95
#     """
#     c0 = contigs[0]
#     colnames = c0.split(sep)[::2]
#
#     # infer types for each column from 1st row
#     # if it can be made a float, assume it is numeric
#     coltypes = []
#     for colval in c0.split(sep)[1::2]:
#         try:
#             float(colval)
#             coltypes.append(float)
#         except ValueError:
#             coltypes.append(str)
#
#     # build a dict of the values
#     contig_dict = dict.fromkeys(colnames)
#     for k in contig_dict:
#         contig_dict[k] = []
#     n = len(contig_dict)
#     for contig in contigs:
#         values = contig.split(sep)[1::2]
#         for i in range(n):
#             value = coltypes[i](values[i])
#             contig_dict[colnames[i]].append(value)
#
#     # create DataFrame from the dict
#     pd.DataFrame.__init__(self, contig_dict)

