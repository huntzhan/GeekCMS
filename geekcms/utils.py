
"""
This package implements tools that can facilitates theme development.
"""

import os
import re
import sys
import configparser
from collections import abc


class SettingsLoader:

    PROJECT_GLOBAL = 'global'

    def __init__(self, path, name=None):
        # settings of project has 'global' as its prefix.
        self.name = name or self.PROJECT_GLOBAL
        # check and save path
        if not os.path.exists(path):
            raise Exception('{} Not Exists.'.format(path))
        self.path = path

    def _load_settings(self):
        config = configparser.ConfigParser()
        with open(self.path) as f:
            config.read_file(f)
        self._config = config

    def get_section(self, section):
        if section in self._config:
            return self._config[section]
        else:
            return None


class _SearchData:

    DATA_FIELD = None
    _vars = {}
    _cache = {}

    @classmethod
    def load_data(cls, loaders):
        # ensure iterable
        if not isinstance(loaders, abc.Iterable):
            loaders = [loaders]
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
    THEMES_KEY = 'Themes'

    @classmethod
    def get_registered_theme_name(cls):
        plain_text = cls.get(cls.THEMES_KEY)
        # yep, name of themes is split by whitespaces.
        theme_names = re.split(r'\s+', plain_text)
        return theme_names


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
    def inputs(cls):
        return cls._join_project(cls.INPUTS)

    @classmethod
    def outputs(cls):
        return cls._join_project(cls.OUTPUTS)

    @classmethod
    def themes(cls):
        return cls._join_project(cls.THEMES)

    @classmethod
    def states(cls):
        return cls._join_project(cls.STATES)

    @classmethod
    def theme_state(cls, theme_name):
        return os.path.join(
            cls.states(),
            theme_name,
        )

    @classmethod
    def theme_dir(cls, theme_name):
        return os.path.join(
            cls.themes(),
            theme_name,
        )

    @classmethod
    def project_settings(cls):
        return cls._join_project(cls.PROJECT_SETTINGS)

    @classmethod
    def theme_settings(cls, theme_name):
        return os.path.join(
            cls.theme_dir(theme_name),
            cls.THEME_SETTINGS,
        )


class SysPathContextManager:

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, *args):
        sys.path.remove(self.path)
