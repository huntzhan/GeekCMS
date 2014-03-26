
import os
import sys
import unittest
import shutil

from geekcms.interface import (_not_in_project, _in_project)
from geekcms.utils import (PathResolver, ShareData,
                           ThemeSettings, ProjectSettings)
from geekcms.protocol import PluginRegister


class TestCLI(unittest.TestCase):

    def setUp(self):
        PluginRegister.clean_up_registered_plugins()
        ProjectSettings.clear()
        ThemeSettings.clear()
        ShareData.clear()
        #force reload
        for key in ['test_theme1', 'test_theme1.plugin',
                    'test_theme2', 'test_theme2.plugin']:
            if key in sys.modules:
                del sys.modules[key]

    def _get_path(self, rel_path):
        path = os.path.join(
            os.getcwd(),
            rel_path,
        )
        return path

    def test_not_in_project(self):
        not_project_path = self._get_path('tests/cases')
        PathResolver.set_project_path(not_project_path)
        template = 'simple'

        sys.argv = ['geekcms', 'startproject', template]

        self.assertEqual(
            _not_in_project(),
            template,
        )
        shutil.rmtree(
            os.path.join(not_project_path, template),
        )

    def test_in_project(self):

        project_path = self._get_path('tests/cases/project')
        PathResolver.set_project_path(project_path)

        sys.argv = ['geekcms', 'run']
        command = _in_project()
        self.assertEqual(
            command,
            'run',
        )

        sys.argv = ['geekcms', 'testcmd', '-a', '-b', 'c', 'd']
        command = _in_project()
        self.assertEqual(
            command,
            'testcmd',
        )
