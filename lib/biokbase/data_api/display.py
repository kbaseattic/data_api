"""
Objects for displaying the results in the IPython notebook.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/1/15'

import pandas as pd
import qgrid

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

class ContigSet(pd.DataFrame):

    DEFAULT_SEP = '_'

    def __init__(self, contigs, sep=DEFAULT_SEP):
        """Create contigset from list of strings.

        Args:
          contigs: List of strings for contigs
          sep: Separator between items packed into each string, e.g.
                      'NODE_48_length_21448_cov_4.91263_ID_95'
        """
        if not contigs:
            pd.DataFrame.__init__(self, {})
            return

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
        self._q = qgrid.show_grid(self, remote_js=nbviewer_mode())

    def _ipython_display_(self):
        return self._q._ipython_display_()
