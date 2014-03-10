
"""
This package implements tools that can facilitates theme development.
"""

import os
import configparser


class SettingsLoader:
    """
    Load settings and provide inquiry interface.
    """

    def __init__(self, name, path):
        self._name = name
        self._path = path

    def _load_settings(self):
        config = configparser.ConfigParser()
        with open(self._path) as f:
            config.read_file(f)
        self._config = config

    def get_section(self, section):
        if section in self._config:
            return self._config[section]
        else:
            return None


class _SearchData:
    """
    Interface to resolve shared data field.
    """

    DATA_FIELD = None
    _vars = {}
    _cache = {}

    @classmethod
    def load_share_data(cls, loaders):
        for loader in loaders:
            cls._vars[loader.name] = loader.get_section(cls.DATA_FIELD)

    @classmethod
    def _access_vars(cls, section_name, key):
        section = cls._cache.get(section_name, None)
        if section:
            val = section.get(key, None)
            return val
        else:
            return None

    @classmethod
    def _generate_key_val_of_vars(cls):
        for section_name, section in cls._vars.items():
            for key, val in section.items():
                yield key, val

    @classmethod
    def _get_cache(cls, key):
        return getattr(cls._cache, key, None)

    @classmethod
    def _set_cache(cls, key, val):
        cls._cache[key] = val

    @classmethod
    def get(cls, search_key):
        # anyway, lookup the cache first.
        val = cls._get_cache(search_key)
        if val:
            return val

        # First way.
        dot_index = search_key.find('.')
        if dot_index != -1 and dot_index != (len(search_key) - 1):
            # prefix with theme name or global.
            section_name = search_key[:dot_index]
            key = search_key[dot_index + 1:]
            val = cls._access_vars(section_name, key)
            if val:
                cls._set_cache(search_key, val)
                return val
        # Second way.
        for key, val in cls._generate_key_val_of_vars():
            if search_key == key:
                cls._set_cache(search_key, val)
                return val
        return None


class ShareDate(_SearchData):

    DATA_FIELD = 'Share'


class ProjectSettings(_SearchData):

    DATA_FIELD = 'RegisterTheme'


class ThemeSettings(_SearchData):

    DATA_FIELD = 'RegisterPlugin'


class PathResolver:

    INPUTS = 'inputs'
    OUTPUTS = 'outputs'
    THEMES = 'themes'
    STATES = 'states'

    PROJECT_SETTINGS = 'settings'
    THEME_SETTINGS = 'settings'

    project_path = None

    @classmethod
    def set_project_path(cls, path):
        cls.project_path = path

    @classmethod
    def _join_project(cls, path):
        return os.path.join(cls.project_path, path)

    @classmethod
    def get_inputs_path(cls):
        return cls._join_project(cls.INPUTS)

    @classmethod
    def get_outputs_path(cls):
        return cls._join_project(cls.OUTPUTS)

    @classmethod
    def get_themes_path(cls):
        return cls._join_project(cls.THEMES)

    @classmethod
    def get_states_path(cls):
        return cls._join_project(cls.STATES)

    @classmethod
    def get_theme_state_path(cls, theme_name):
        return os.path.join(
            cls.get_states_path(),
            theme_name,
        )

    @classmethod
    def get_theme_code_path(cls, theme_name):
        return os.path.join(
            cls.get_themes_path(),
            theme_name,
        )

    @classmethod
    def get_project_settings_path(cls):
        return cls._join_project(cls.PROJECT_SETTINGS)

    @classmethod
    def get_theme_settings_path(cls, theme_name):
        return os.path.join(
            cls.get_theme_code_path(theme_name),
            cls.THEME_SETTINGS,
        )
