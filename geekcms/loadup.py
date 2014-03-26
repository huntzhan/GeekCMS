
import os
import importlib
from collections import OrderedDict

from .utils import (SettingsLoader, ProjectSettings, ThemeSettings,
                    ShareData, PathResolver, SysPathContextManager)
from .protocol import PluginRegister
from .sequence_analyze import SequenceParser


class SettingsProcedure:

    @classmethod
    def _load_share_data(cls, loaders):
        ShareData.load_data(loaders)

    @classmethod
    def _load_project_settings(cls, path):
        project_settings_loader = SettingsLoader(path)
        ProjectSettings.load_data(project_settings_loader)
        cls._load_share_data(project_settings_loader)

    @classmethod
    def _load_theme_settings(cls, path, name):
        theme_settings_loader = SettingsLoader(path, name)
        ThemeSettings.load_data(theme_settings_loader)
        cls._load_share_data(theme_settings_loader)

    @classmethod
    def _load_settings(cls):
        pr = PathResolver

        # set up ProjectSettings
        project_settings_path = pr.project_settings()
        cls._load_project_settings(project_settings_path)

        # set up ThemeSettings
        theme_settings_set = []
        for theme_name in ProjectSettings.get_registered_theme_name():
            theme_settings_path = pr.theme_settings(theme_name)
            cls._load_theme_settings(theme_settings_path, theme_name)

    @classmethod
    def _load_themes(cls):
        pr = PathResolver

        theme_dir = pr.themes()
        for theme_name in ProjectSettings.get_registered_theme_name():
            with SysPathContextManager(theme_name, theme_dir):
                importlib.import_module(theme_name)

    @classmethod
    def run(cls, project_path=None):
        # project_path is None means the path has already been set.
        if project_path:
            PathResolver.set_project_path(project_path)
        cls._load_settings()
        cls._load_themes()


class PluginProcedure:
    runtime_components = ['pre_load', 'in_load', 'post_load',
                          'pre_process', 'in_process', 'post_process',
                          'pre_write', 'in_write', 'post_write']

    extended_procedure = ['cli_extend']

    @classmethod
    def _get_plain_text(cls, theme_name, field_name):
        search_key = '{}.{}'.format(theme_name, field_name)
        plain_text = ThemeSettings.get(search_key)
        return plain_text

    @classmethod
    def _get_execution_orders(cls):
        error_happend = False
        exec_orders = OrderedDict()

        # In this function, exec_orders contains both default and extended
        # procedures.
        for component in (cls.runtime_components + cls.extended_procedure):
            parser = SequenceParser()
            for theme_name in ProjectSettings.get_registered_theme_name():
                plain_text = cls._get_plain_text(theme_name, component)
                if plain_text is None:
                    continue
                # analyze
                parser.analyze(theme_name, plain_text)

            if parser.error:
                parser.report_error()
                error_happend = True
            else:
                exec_orders[component] = parser.generate_sequence()

        return error_happend, exec_orders

    @classmethod
    def _linearize_exec_orders(cls, exec_orders):
        # extract cli_indices.
        extract_field = cls.extended_procedure[0]
        cli_indices = exec_orders[extract_field]
        del exec_orders[extract_field]
        # generate plugin calling sequence.
        flat_orders = []
        for container in exec_orders.values():
            flat_orders.extend(container)
        return flat_orders, cli_indices

    @classmethod
    def _verify_plugins(cls, flat_orders):
        for plugin_index in flat_orders:
            plugin = PluginRegister.get_plugin(plugin_index)
            if plugin is None:
                # can not find such plugin
                print('Can Not Find {}'.format(plugin_index))
                return True
        return False

    @classmethod
    def run(cls):
        parse_error, exec_orders = cls._get_execution_orders()
        flat_order, cli_indices = cls._linearize_exec_orders(exec_orders)
        match_error = cls._verify_plugins(flat_order + cli_indices)
        if parse_error or match_error:
            raise SyntaxError('Error happended, suspend program.')
        return flat_order, cli_indices
