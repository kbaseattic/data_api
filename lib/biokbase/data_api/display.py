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

    # def __rb_parsing(self):
    #     """Saved some parsing of what was found
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

class TemplateMixin(object):
    template = ''
    def __init__(self):
        self._template = Template(self.template)

    def render(self, *args, **kwargs):
        return self._template.render(*args, **kwargs)

class Classification(TemplateMixin):
    """Taxonomic classification.
    """
    template = '''{% for name in classification %}
    <span style="margin-left: {{ loop.index0 * 10 }}px">
    <span style="font-size: 50%">&gt;</span>&nbsp;{{ name }}
    </span><br>{% endfor %}'''

    def __init__(self, taxon):
        """Create from a taxon.

        Args:
          taxon: TaxonAPI object.
        """
        TemplateMixin.__init__(self)
        if taxon is None:
            self.classf = []
            return
        children = taxon.get_children() or []
        tx, parents = taxon, []
        while tx:
            tx = tx.get_parent()
            if tx:
                parents.insert(tx.get_scientific_name(), 0)
        self.classf = parents + [taxon.get_scientific_name()] + children

    def _repr_html_(self):
        return self.render(classification=self.classf)

class Organism(TemplateMixin):
    """Summary of an organism as per ENSEMBL page, from
    a TaxonAPI.
    """
    template = '''<b>Taxonomy ID</b>: {{taxon.get_taxonomic_id()}}<br>
        <b>Name</b>: {{taxon.get_scientific_name()}}<br>
        <b>Aliases</b>:<br>
        {% for a in taxon.get_aliases() %}
        &nbsp;&nbsp;{{ a }}<br>
        {% endfor %}
        <b>Classification</b>:<br>''' + \
        Classification.template

    def __init__(self, taxon):
        """Create from a taxon.

        Args:
          taxon: TaxonAPI object.
        """
        TemplateMixin.__init__(self)
        self.taxon = taxon

    def _repr_html_(self):
        if self.taxon is None:
            return None
        classf = Classification(self.taxon).classf
        return self.render(classification=classf, taxon=self.taxon)

class AssemblyInfo(TemplateMixin):
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