"""
Objects for displaying the results in the IPython notebook.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '8/1/15'

# Stdlib
import logging

# Third-party
from IPython.display import display
import matplotlib.pyplot as plt
import pandas as pd
# Qgrid table display
try:
    import qgrid
    qgrid.nbinstall()
except ImportError:
    qgrid = None
from jinja2 import Template
# Seaborn graphing
try:
    import seaborn as sns
    sns.set_style("whitegrid")
except ImportError:
    sns = None

# Local
from doekbase.data_api.util import get_logger, log_start, log_end

_log = get_logger('doekbase.data_api.display')

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
            print
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
        self.classification = self.taxon.get_scientific_lineage().split(';')
        self.name = self.taxon.get_scientific_name()
        # self.children = self.taxon.get_children() or []
        # tx, self.parents = self.taxon, []
        # while tx:
        #     tx = tx.get_parent()
        #     if tx:
        #         self.parents.insert(tx.get_scientific_name(), 0)
        # self.classification = self.parents + [self.name] + [
        #     child.get_scientific_name() for child in self.children]

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
          ga: GenomeAnnotation object
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

class FeaturePositions(Table):
    """The position (and ID and type) of features in the genome.
    """

    def __init__(self, ga):
        """Create from a genome.

        Args:
          ga: GenomeAnnotation object
        """
        data = self._get_features(ga)
        Table.__init__(self, data, columns=('type', 'id', 'start', 'len', 'dir'))

    def _get_features(self, ga):
        "This should probably move into genome_annotation module"
        from doekbase.data_api.object import ObjectAPI
        fcr = 'feature_container_references'
        refs = ga.get_data_subset(path_list=[fcr])[fcr]
        result = []
        for ref in refs.values():
            obj = ObjectAPI(ga.services, ref) # fetch data
            features = obj.get_data()['features']
            for feat_id in features.keys():  # iterate features
                ftype = features[feat_id]['type']
                for loc in features[feat_id]['locations']:
                    # biuld an output row and add to result
                    row = (ftype, feat_id, loc[1], loc[3], loc[2])
                    result.append(row)
        return result

    def stripplot(self):
        """Make a 'stripplot' of all feature positions.

        Requires the 'seaborn' library
        """
        if sns is None:
            raise NotImplementedError('Requires the "seaborn" library. See: '
                             'https://github.com/mwaskom/seaborn')
        ax = sns.stripplot(x='start', y='type', data=self)
        # get rid of spurious negative tick
        ax.set_xlim(0, ax.get_xlim()[1])
        return ax


class ProteinStats(Table):
    """Various statistics for proteins.
    """
    STATS_LENGTH = 'length'

    def __init__(self, ga, stats=[STATS_LENGTH]):
        """Create from a genome.

        Args:
          ga: GenomeAnnotation object
        """
        proteins = ga.get_proteins()
        data = {}
        if self.STATS_LENGTH in stats:
            data[self.STATS_LENGTH] = [
                len(v['amino_acid_sequence'])
                for v in proteins.values()]
        Table.__init__(self, data)

    def plot_protein_lengths(self):
        return self.plot(x=self.STATS_LENGTH, kind='hist')

class GenomeSummary(TemplateMixin):
    """Summary of a GenomeAnnotation.

    Attributes:
       taxon (dict): Information about the taxonomic type
       assembly (dict): Infomration about the contigs in the assembly
       annotation (dict): Information about the assembly
       data (dict): All the information as a single dict with the attributes
                    listed above as top-level keys.
    """
    template = '<h3>Genome Summary</h3>'+ Organism.template

    def __init__(self, ga, taxons=True, assembly=True, annotation=True):
        """Create new summary from GenomeAnnotation.

        Args:
          ga (GenomeAnnotation): input object
          taxons: If False, do not retrieve taxons
          assembly: If False, do not retrieve assembly
          annotation: If False, do not retrieve annotation
        """
        if not hasattr(ga, 'get_taxon') or not hasattr(ga, 'get_assembly'):
            raise TypeError('{} is not a recognized GenomeAnnotation type.'
                .format(type(ga)))

        self.data = { 'taxon': {}, 'assembly': {}, 'annotation': {}}
        if taxons:
            self.data['taxon'] = self._get_taxon(ga)
        if assembly:
            self.data['assembly'] = self._get_assembly(ga)
        if annotation:
            self.data['annotation'] = self._get_annotation(ga)

        self.ga = ga
        self._set_attrs()

    def _set_attrs(self):
        """Set attributes for top-level keys"""
        for key, value in self.data.items():
            setattr(self, key, value)

        TemplateMixin.__init__(self)

    @staticmethod
    def _get_taxon(ga):
        t0 = log_start(_log, 'get_taxon')
        try:
            taxon = ga.get_taxon()
        except Exception as err:
            raise RuntimeError('Cannot get taxon: {}'.format(err))
        txn = { k: getattr(taxon, 'get_' + k)()
                 for k in ('taxonomic_id', 'kingdom', 'domain',
                           'genetic_code', 'scientific_name', 'aliases',
                           'scientific_lineage')}
        txn['lineage_list'] = txn['scientific_lineage'].split(';')
        log_end(_log, t0, 'get_taxon')
        return txn

    @staticmethod
    def _get_assembly(ga):
        t0 = log_start(_log, 'get_assembly')
        try:
            assembly = ga.get_assembly()
        except Exception as err:
            raise RuntimeError('Cannot get assembly: {}'.format(err))
        asy = {
            k1: getattr(assembly, 'get_' + k2)()
            for k1, k2 in (
                ('number_of_contigs', 'number_contigs'),
                ('total_length', 'dna_size'),
                ('total_gc_content', 'gc_content'),
                ('contig_length', 'contig_lengths'),
                ('contig_gc_content', 'contig_gc_content')
            )}
        log_end(_log, t0, 'get_assembly')
        return asy

    @staticmethod
    def _get_annotation(ga):
        t0 = log_start(_log, 'get_annotation')
        try:
            feature_types = ga.get_feature_types()
        except Exception as err:
            raise RuntimeError('Cannot get feature_types: {}'.format(err))
        ann = { 'feature_' + k: getattr(ga, 'get_feature_' + k)(feature_types)
                for k in ('type_descriptions', 'type_counts')}
        ann['feature_types'] = feature_types
        log_end(_log, t0, 'get_annotation')
        return ann

    def summary_plots(self):
        """Show some plots summarizing the information in the Genome.
        """
        # First plot: feature types and counts
        n = sum(map(bool, self.data.keys()))
        i = 1
        plt.close()
        if self.annotation:
            plt.subplot(n, 1, i)
            self._plot_feature_counts()
            i += 1
        # Second plot
        if self.assembly:
            plt.subplot(n, 1, i)
            self._plot_contig_lengths()
            i += 1
        # Third plot
        if self.assembly:
            plt.subplot(n, 1, i)
            self._plot_contig_gc()
            i += 1
        plt.show()

    def _plot_feature_counts(self):
        d = pd.DataFrame({'Feature Type': self.annotation['feature_types'],
                          'Count': self.annotation['feature_type_counts']})
        ax = sns.barplot(x='Count', y='Feature Type', orient='h', data=d)
        ax.set_title('Feature type counts from {} to{}'.format(min(d['Count']),
                                                               max(d['Count'])))

    def _plot_contig_lengths(self):
        vals = pd.Series(self.assembly['contig_length'].values(),
                         name='Sequence length (bp)')
        ax = sns.distplot(vals)
        ax.set_title('Contig lengths from {} to {}'.format(
            vals.min(), vals.max()))

    def _plot_contig_gc(self):
        gc = self.assembly['contig_gc_content'].values()
        gcp, ctg = 'GC percent', 'Contigs'
        d = pd.DataFrame({gcp: [x*100.0 for x in sorted(gc)],
                          ctg: range(1, len(gc) + 1)})
        ax = sns.factorplot(x=gcp, y=ctg, data=d)
        #ax.set_title("Contig {} from {.2f} to {.2f}"
        #             .format(gcp, min(gc), max(gc)))
        return ax

    def _repr_html_(self):
        self.summary_plots()
        classf = Classification(self.taxon).classification
        return self.render(classification=classf, taxon=self.taxon)

