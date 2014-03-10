
"""
This package implements tools that can facilitates theme development.
"""


import configparser


class SettingsLoader:
    """
    Load settings and provide inquiry interface.
    """

    # SHARE_FIELD = 'Share'
    # THEME_FIELD = 'Theme'
    # PLUGIN_REGISTRATION_FIELD = 'Plugin'

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

    # def get_share_data(self):
    #     return self.get_section(self.SHARE_FIELD)

    # def get_registered_theme(self):
    #     return self.get_section(self.THEME_FIELD)

    # def get_registered_plugin(self):
    #     return self.get_section(self.PLUGIN_REGISTRATION_FIELD)


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


class ProjectSettings:

    DATA_FIELD = 'RegisterTheme'


class ThemeSettings:

    DATA_FIELD = 'RegisterPlugin'
