"""
Nose testing plugin for configuring Workspace URL during tests.
"""
# Imports

# Stdlib
import os
# Third-party
from nose.plugins import Plugin
# Local
from doekbase.data_api import core
from doekbase.data_api.util import get_logger

# Logging
_log = get_logger(__name__)

class WorkspaceURL(Plugin):
    """Plugin that sets up the Workspace mocking instead of the
    'real' workspace for all tests.
    """
    def options(self, parser, env):
        """Register commmandline options.
        """
        _log.info('WorkspaceURL.options')
        # Shock URL
        parser.add_option(
            "--shock-url", dest="shock_url", metavar='URL',
            default='https://ci.kbase.us/services/shock-api/',
            help="Shock URL [%default]")
        # Workspace URL (or path)
        parser.add_option(
            "--ws-url", dest="ws_url", metavar='URL or PATH',
            default='https://ci.kbase.us/services/ws/',
            help="Workspace URL, which may be either a "
                 "server address or directory path to indicate that "
                 "tests should use the file-based workspace with "
                 "all files in that path. [%default]")
        # File workspace format (JSON or MessagePack)
        parser.add_option(
            "--wsfile-msgpack", dest="wsfile_msgpack",
            action='store_true', default=False,
            help="If the file-based workspace is being used, "
                 "look for and decode MessagePack-formatted "
                 "files ending in '.msgpack'. By default, look for "
                 "JSON files ending in '.json'")

    def configure(self, options, conf):
        """Configure plugin.
        """
        _log.info('WorkspaceURL.configure, ws_url={}'.format(options.ws_url))
        if not self.can_configure:
            _log.error('Cannot configure')
            return
        # Assign parsed values to global variables in the 'core' module.
        core.g_ws_url = options.ws_url
        core.g_shock_url = options.shock_url
        core.g_use_msgpack = options.wsfile_msgpack
        # Set instance state and return
        self.enabled = True
        self.conf = conf
