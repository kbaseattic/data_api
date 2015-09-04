"""
Nose testing plugin for turning on the Workspace mocking for
all tests.
"""
# Imports

# stdlib
import glob
import os; opj = os.path.join
# third-party
from nose.plugins import Plugin
# local
from biokbase.data_api.tests.shared import g_ws_mock
from biokbase.data_api import wsmock

##
## NOT TESTED!! WORK IN PROGRESS!!
##

class UseWorkspaceMock(Plugin):
    """Plugin that sets up the Workspace mocking instead of the
    'real' workspace for all tests.
    """
    def options(self, parser, env):
        """Register commmandline options.
        """
        parser.add_option(
            "--wsmock", dest="wsmock_dir", metavar='DIR',
            default=env.get('KB_MOCK_DIR'),
             help="Use mock workspace, initialized with all "
            " files at DIR [KB_MOCK_DIR]")

    def configure(self, options, conf):
        """Configure plugin.
        """
        global g_ws_mock
        if not self.can_configure:
            return
        if options.wsmock_dir:
            mock = wsmock.WorkspaceMock()
            input_files = glob.glob(opj(options.wsmock_dir, '*.json'))
            if len(input_files) == 0:
                raise ValueError('No .json files found for KBase Workspace '
                                 'mock in path "{}"'.format(options.wsmock_dir))
            for f in input_files:
                mock.put(f)
            g_ws_mock = mock
        self.enabled = g_ws_mock is not None
        self.conf = conf
