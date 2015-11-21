"""
Test Workspace client
"""
__author__ = 'dang'

## Imports
# System
import logging
import time
import unittest
# Local
from . import shared
from doekbase.data_api import core, wsfile
from doekbase.workspace import client as ws_client

_log = logging.getLogger('doekbase.tests.test_ws_client')

genome_new = "ReferenceGenomeAnnotations/kb|g.166819"
genome_old = "OriginalReferenceGenomes/kb|g.166819"
taxon_new = "ReferenceTaxons/242159_taxon"
taxon_old = "OriginalReferenceGenomes/kb|g.166819"

def generic_object():
    """Get a generic object."""
    return {'type': 'Empty.AType-1.0',
            'data': {'hello': 'world'}}

NOT_SUPPORTED_MSG = 'Not supported by local Workspace implementation'

class WorkspaceTests(unittest.TestCase):
    # maximum allowable version of workspace for this
    # test suite to be valid
    MAX_WS_VERSION = (0, 999, 999)

    is_local = '://' not in core.g_ws_url

    def setUp(self):
        if self.is_local:
            self.ws = wsfile.WorkspaceFile(shared.g_ws_url)
            for ref in (genome_new, genome_old, taxon_new, taxon_old):
                self.ws.load(ref.replace('/', '_'))
        else:
            self.ws = ws_client.Workspace(
                url=shared.g_ws_url, token=shared.token)
        self._my_ws = None
        self._delete_ws = set()

    def tearDown(self):
        if not self.is_local:
            # delete temporary workspaces
            for ws in self._delete_ws:
                _log.info('deleting temporary workspace: {}'.format(ws))
                self.ws.delete_workspace({'workspace': ws})

    def get_workspace(self, use_existing=True):
        if use_existing and self._my_ws is not None:
            return self._my_ws
        name = 'foo-{:.3f}'.format(time.time())
        ws_obj = self.ws.create_workspace({'workspace': name})
        self._delete_ws.add(name)
        if use_existing:
            self._my_ws = ws_obj
        return name

    def test_ver(self):
        value = self.ws.ver()
        p = value.split('.')
        assert len(p) == 3, 'Bad version number: {}'.format(value)
        for i in range(3):
            assert int(p[i]) <= self.MAX_WS_VERSION[i], \
                "Version mismatch: {ver} > {expected}".format(
                    ver=value, expected='.'.join(map(str, self.MAX_WS_VERSION)))

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_create_workspace(self):
        self.get_workspace()

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_alter_workspace_metadata(self):
        name = self.get_workspace(False)
        self.ws.alter_workspace_metadata({'wsi': {'workspace': name},
                                          'new': {'trump': 'idiot'}})

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_clone_workspace(self):
        name = self.get_workspace()
        name2 = 'bar-{:.3f}'.format(time.time())
        self.ws.clone_workspace({'wsi': {'workspace': name},
                                 'workspace': name2})
        self._delete_ws.add(name2)

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_lock_workspace(self):
        # this is not reversible and the workspace cannot
        # be deleted (!), so running this as a test against a
        # real workspace creates cruft.
        # name = self.test_create_workspace()
        # self.ws.lock_workspace({'workspace': name})
        return

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_workspacemeta(self):
        # deprecated form of get_workspace_info
        return

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_workspace_info(self):
        name = self.get_workspace()
        self.ws.get_workspace_info({'workspace': name})

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_workspace_description(self):
        name = self.get_workspace()
        self.ws.get_workspace_description({'workspace': name})

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_set_permissions(self):
        name = self.get_workspace(False)
        self.ws.set_permissions({'workspace': name,
                                 'new_permission': 'r',
                                 'users': ['kbasetest']})

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_set_global_permission(self):
        name = self.get_workspace(False)
        self.ws.set_global_permission({'workspace': name,
                                       'new_permission': 'r'})

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_set_workspace_description(self):
        name = self.get_workspace()
        self.ws.set_workspace_description(
            {'workspace': name, 'description': 'quite lame'})

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_permissions(self):
        name = self.get_workspace()
        self.ws.get_permissions({'workspace': name})

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_save_objects(self):
        name = self.get_workspace()
        self.ws.save_objects({
            'workspace': name, 'objects': [generic_object()]
        })

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_administer(self):
        try:
            self.ws.administer({})
        except ws_client.ServerError as err:
            # fail if this is NOT the "normal" error
            # caused by lack of admin. permissions
            assert 'not an admin' in str(err)

"""
    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_object_provenance(self):
        assert False

    def test_get_objects(self):
        assert False

    def test_get_object_subset(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_object_history(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_list_referencing_objects(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_list_referencing_object_counts(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_referenced_objects(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_list_workspaces(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_list_workspace_info(self):
        assert False

    def test_list_workspace_objects(self):
        assert False

    def test_list_objects(self):
        assert False

    def test_get_objectmeta(self):
        assert False

    def test_get_object_info(self):
        assert False

    def test_get_object_info_new(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_rename_workspace(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_rename_object(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_copy_object(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_revert_object(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_hide_objects(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_unhide_objects(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_delete_objects(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_undelete_objects(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_delete_workspace(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_undelete_workspace(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_request_module_ownership(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_register_typespec(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_register_typespec_copy(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_release_module(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_list_modules(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_list_module_versions(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_module_info(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_jsonschema(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_translate_from_MD5_types(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_translate_to_MD5_types(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_type_info(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_all_type_info(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_func_info(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_get_all_func_info(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_grant_module_ownership(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_remove_module_ownership(self):
        assert False

    @unittest.skipIf(is_local, NOT_SUPPORTED_MSG)
    def test_list_all_types(self):
        assert False

"""


