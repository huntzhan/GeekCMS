import unittest
import os
import re
import configparser
from collections import defaultdict

from geekcms.parser.simple_lex import lexer
from geekcms.parser.simple_yacc import parser
from geekcms.protocal import PluginIndex
from geekcms.sequence_analyze import SequenceParser


class PLYTest(unittest.TestCase):

    def test_parser(self):
        pass


_THEME = 'testtheme'


class SequenceParserTest(unittest.TestCase):

    def _get_suppose_result(self, text):
        result = re.sub(r'\s', '', text).split(',')

        def fix(item):
            if '.' not in item:
                return PluginIndex(_THEME, item)
            else:
                theme, plugin = item.split('.')
                return PluginIndex(theme, plugin)

        return list(map(fix, result))

    def _load_test_case(self, name):
        dir_path = os.path.join(os.path.dirname(__file__), 'cases/parser')
        file_path = os.path.join(dir_path, name)

        config = configparser.ConfigParser()
        with open(file_path) as f:
            config.read_file(f)
        section = config['Test']
        return section['case'], self._get_suppose_result(section['result'])

    def test_parser_with_good_case(self):
        cases = ['case1', 'case2', 'case3', 'case4']
        for case in cases:
            text, suppose_result = self._load_test_case(case)
            parser = SequenceParser()
            parser.analyze(_THEME, text)
            result = parser.generate_sequence()
            self.assertListEqual(result, suppose_result)
