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

    def __rb_parsing(self):
        """Saved some parsing of what was found
        in a Rhodobacter genome.
            NODE_48_length_21448_cov_4.91263_ID_95
        """
        c0 = contigs[0]
        colnames = c0.split(sep)[::2]

        # infer types for each column from 1st row
        # if it can be made a float, assume it is numeric
        coltypes = []
        for colval in c0.split(sep)[1::2]:
            try:
                float(colval)
                coltypes.append(float)
            except ValueError:
                coltypes.append(str)

        # build a dict of the values
        contig_dict = dict.fromkeys(colnames)
        for k in contig_dict:
            contig_dict[k] = []
        n = len(contig_dict)
        for contig in contigs:
            values = contig.split(sep)[1::2]
            for i in range(n):
                value = coltypes[i](values[i])
                contig_dict[colnames[i]].append(value)

        # create DataFrame from the dict
        pd.DataFrame.__init__(self, contig_dict)

class Classification(object):
    __template = Template('''<h2>Classification</h2>
    <ul>
    {% for name in classification %}
    <li style="margin-left: {{ loop.iter0 * 10 }}">
    {{ name }}
    </li>
    {% endfor %}
    </ul>
    ''')
    def __init__(self, taxon):
        children = taxon.get_children() or []
        tx, parents = taxon, []
        while tx:
            tx = tx.get_parent()
            if tx:
                parents.insert(tx.get_scientific_name(), 0)
        self.classf = parents + [taxon.get_scientific_name()] + children

    def _repr_html_(self):
        return self.__template.render(classification=self.classf)