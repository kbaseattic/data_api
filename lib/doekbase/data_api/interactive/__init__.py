"""
Package for interactive usage such as in the IPython/Jupyter notebook.

Modules in this package are separated out because they have heavyweight
dependencies such as numpy, matplotlib, pandas, seaborn, bokeh, etc.
that are not needed for the Data API when it is used as a server or
programmatically inside a non-interactive program.

Therefore, installing this sub-package is optional and enabled with flags
documented in the top-level distutils setup.py and README.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '10/15/15'

