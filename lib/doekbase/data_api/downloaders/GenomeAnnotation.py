"""
GenomeAnnotation to GenBank downloader.


Usage::

    from doekbase.data_api.downloaders import GenomeAnnotation

    # Genome annotation
    obj = genome.GenomeConverter(ref='6052/40/1', kbase_instance='ci')
    new_obj_ref = obj.convert(target_workspace_id)
    # NOTE: side-effect of this conversion is to also create a ContigSet
    # object, by converting the associated Assembly, in the same workspace.

    # Assembly
    obj = genome.AssemblyConverter(ref='6052/31/1', kbase_instance='ci')
    new_obj_ref = obj.convert(target_workspace_id)
"""
__author__ = 'Marcin Joachimiak <mjoachimiak@lbl.gov>'
__date__ = '6/10/16'

# Stdlib
import hashlib
import itertools
import logging
# Local
from . import base
from .base import DEBUG, INFO, WARN, ERROR
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.pbar import PBar


def downloadAsGBK():

  return None