
import unittest
from docopt import docopt

from geekcms.doc_construct import DocConstructor
from geekcms.protocol import BaseExtendedProcedure


class DocConstructorTest(unittest.TestCase):

    def test_doc_not_in_project(self):
        doc = DocConstructor.get_doc_not_in_project()
        argv = ['startproject', 'default']
        args = docopt(doc, argv)

        self.assertEqual(
            args['<template_name>'],
            'default',
        )

    def test_in_project_with_extended_plugin(self):

        class TestPlugin(BaseExtendedProcedure):

            def get_command_and_explanation(self):
                return 'testcmd', 'this is a test command'

        doc, mapping = DocConstructor.get_doc_and_cli_mapping([TestPlugin()])
        argv = ['testcmd', '-a', '-b', 'c', 'd']
        args = docopt(doc, argv, options_first=True)

        self.assertEqual(
            args['<command>'],
            'testcmd',
        )
        self.assertListEqual(
            args['<args>'],
            ['-a', '-b', 'c', 'd'],
        )
