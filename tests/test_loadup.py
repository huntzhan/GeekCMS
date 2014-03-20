
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


class _GetCasePath:

    def _get_file_path(self, rel_path):
        test_dir = os.path.join(
            os.getcwd(),
            'tests/cases/project',
        )

        path = os.path.join(
            test_dir,
            rel_path,
        )
        return path

class SettingsProcedureTest(unittest.TestCase, _GetCasePath):

    def test_run(self):
        project_path = self._get_file_path('')
        SettingsProcedure.run(project_path)
