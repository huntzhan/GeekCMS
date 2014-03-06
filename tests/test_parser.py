import unittest
import re
from collections import defaultdict
from geekcms import sequence_analyze


class PreParserTest(unittest.TestCase):

    def _compile(self, pattern):
        fixed_pattern = r'^{}$'.format(pattern)
        return re.compile(fixed_pattern, re.ASCII)

    def _get_match_set(self, cases, extract_key, parser):
        result = set()
        for item in cases:
            m = parser.match(item)
            if m:
                result.add(m.group(extract_key))
        return result

    def test_regex_definition_basic(self):
        lib = sequence_analyze

        # identifier
        full = ['_', '8a', 'abc)d', 'abc_d', 'abc']
        good = {'_', 'abc_d', 'abc'}
        p = self._compile(lib._IDENTIFIER)
        result = self._get_match_set(full, 'identifier', p)
        self.assertSetEqual(result, good)

        # right op
        p = self._compile(lib._RIGHT_OP)
        m = p.match('>>')
        self.assertEqual(m.group('right_op'), '>>')

        # left op
        p = self._compile(lib._LEFT_OP)
        m = p.match('<<')
        self.assertEqual(m.group('left_op'), '<<')

        # decimalinteger
        full = ['123', '0800', '000000', 'abc']
        good = {'123', '000000'}
        p = self._compile(lib._DECIMAL)
        result = self._get_match_set(full, 'decimalinteger', p)
        self.assertSetEqual(result, good)

        # left relation
        full = ['<<', '<<1', '<<0', '<']
        good = {'<<', '<<1', '<<0'}
        p = self._compile(lib._LEFT_REL)
        result = self._get_match_set(full, 'left_relation', p)
        self.assertSetEqual(result, good)

        # right relation
        full = ['>>', '1>>', '0>>', '>', '>>1']
        good = {'>>', '1>>', '0>>'}
        p = self._compile(lib._RIGHT_REL)
        result = self._get_match_set(full, 'right_relation', p)
        self.assertSetEqual(result, good)

    def test_regex_definition_combination(self):
        lib = sequence_analyze
