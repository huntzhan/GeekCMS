
"""
Test Plan.

SettingsLoader:
    test_init:
        1. with name.
        2. without name.
    test_not_found:
        initialize loader with file not existed, expect failure.

_SearchData, ShareData, ProjectSettings, ThemeSettings:
    test_search_with_prefix:
        1. theme prefix(i.e. 'theme.variable').
        2. global prefix.
    test_search_without_prefix:
        ...
    test_theme_names_retrieving:
        ...

PathResolver:
    test_inputs_outputs:
        ...
    test_themes_states:
        ...
    test_theme_state_and_dir:
        ...
    test_project_and_theme_settings:
        ...
"""

import unittest
import os

from geekcms.utils import (SettingsLoader, ShareData, ProjectSettings,
                           PathResolver, check_cwd_is_project)


class _GetCasePath:

    def _get_file_path(self, rel_path):
        test_dir = os.path.join(
            os.getcwd(),
            'tests/cases/loader',
        )

        path = os.path.join(
            test_dir,
            rel_path,
        )
        return path


class SettingsLoaderTest(unittest.TestCase, _GetCasePath):

    def test_init(self):
        case_path = self._get_file_path('case1')
        theme = 'testtheme'

        loader_with_name = SettingsLoader(case_path, theme)
        loader_without_name = SettingsLoader(case_path)

        self.assertEqual(loader_with_name.name, theme)
        self.assertEqual(loader_without_name.name, 'global')

    @unittest.expectedFailure
    def test_not_found(self):
        case_path = self._get_file_path('CASE_DO_NOT_EXISTED')
        loader = SettingsLoader(case_path)


class DataSearchTest(unittest.TestCase, _GetCasePath):

    def setUp(self):
        case_path = self._get_file_path('case1')
        self.theme = 'testtheme'
        self.loader = SettingsLoader(case_path, self.theme)
        self.global_loader = SettingsLoader(case_path)

    def _get_search_key(self, theme, key):
        return '{}.{}'.format(theme, key)

    def test_search_with_prefix(self):
        ShareData.clear()
        ShareData.load_data(self.loader)

        self.assertEqual(
            ShareData.get(self._get_search_key(self.theme, 'a')),
            '1',
        )
        self.assertEqual(
            ShareData.get(self._get_search_key(self.theme, 'b')),
            '2',
        )
        self.assertEqual(
            ShareData.get(self._get_search_key(self.theme, 'c')),
            '3',
        )

    def test_global_search(self):
        ShareData.clear()
        ShareData.load_data(self.global_loader)

        self.assertEqual(
            ShareData.get(self._get_search_key('global', 'a')),
            '1',
        )
        self.assertEqual(
            ShareData.get(self._get_search_key('global', 'b')),
            '2',
        )
        self.assertEqual(
            ShareData.get(self._get_search_key('global', 'c')),
            '3',
        )

    def test_search_without_prefix(self):
        ShareData.clear()
        ShareData.load_data(self.loader)

        self.assertEqual(
            ShareData.get('a'),
            '1',
        )
        self.assertEqual(
            ShareData.get('b'),
            '2',
        )
        self.assertEqual(
            ShareData.get('c'),
            '3',
        )

    def test_theme_names_retrieving(self):
        ProjectSettings.clear()
        case_path = self._get_file_path('case2')
        loader = SettingsLoader(case_path)

        ProjectSettings.load_data(loader)

        self.assertListEqual(
            list(ProjectSettings.get_registered_theme_name()),
            ['a', 'b', 'c', 'd', 'e', 'f'],
        )


class PathResolverTest(unittest.TestCase, _GetCasePath):

    def setUp(self):
        self.project_path = self._get_file_path('')
        PathResolver.set_project_path(self.project_path)

    def test_top_level_names(self):
        names = ['inputs', 'outputs', 'themes', 'states']
        for name in names:
            self.assertEqual(
                getattr(PathResolver, name)(),
                self._get_file_path(name),
            )

    def test_theme_state_and_dir(self):
        self.assertEqual(
            PathResolver.theme_state('testtheme'),
            self._get_file_path('states/testtheme'),
        )
        self.assertEqual(
            PathResolver.theme_dir('testtheme'),
            self._get_file_path('themes/testtheme'),
        )

    def test_project_and_theme_settings(self):
        self.assertEqual(
            PathResolver.project_settings(),
            self._get_file_path('settings'),
        )
        self.assertEqual(
            PathResolver.theme_settings('testtheme'),
            self._get_file_path('themes/testtheme/settings'),
        )

    def test_check_cwd_is_project(self):
        not_project_path = self._get_file_path('')
        project_path = os.path.join(
            os.getcwd(),
            'tests/cases/project',
        )

        PathResolver.set_project_path(not_project_path)
        self.assertFalse(check_cwd_is_project())

        PathResolver.set_project_path(project_path)
        self.assertTrue(check_cwd_is_project())
