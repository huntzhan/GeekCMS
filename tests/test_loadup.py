
"""
Test Plan.

SettingsProcedure
    test_run:
        ...

PluginProcedure
    test_run:
        ...

"""


import os
import unittest
from geekcms.loadup import (SettingsProcedure, PluginProcedure)
from geekcms.utils import (ShareData, ProjectSettings, ThemeSettings)
from geekcms.protocal import (PluginRegister, PluginIndex)


class ProcedureTest(unittest.TestCase):

    def setUp(self):
        ShareData.clear()
        ProjectSettings.clear()
        ThemeSettings.clear()
        PluginRegister.clean_up_registered_plugins()

        self.project_path = os.path.join(
            os.getcwd(),
            'tests/cases/project',
        )

    def test_settings_run(self):
        SettingsProcedure.run(self.project_path)

        self.assertSetEqual(
            set(ProjectSettings.get_registered_theme_name()),
            set(['test_theme1', 'test_theme2']),
        )
        self.assertSetEqual(
            set(ThemeSettings._vars),
            set(['test_theme1', 'test_theme2']),
        )

    def test_plugin_run(self):
        SettingsProcedure.run(self.project_path)
        flat_orders, cli_indices = PluginProcedure.run()

        self.assertSetEqual(
            set(flat_orders),
            set([PluginIndex('test_theme1', 'a'),
                 PluginIndex('test_theme2', 'b')]),
        )
        self.assertSetEqual(
            set(cli_indices),
            set([PluginIndex('test_theme1', 'test_cli')]),
        )
