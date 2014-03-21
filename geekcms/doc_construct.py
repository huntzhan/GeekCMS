
import os


_DOC_TEMPLATE_IN_PROJECT = """
Usage:
    geekcms <command> [<args>...]

Avaliable Commands:
    run  default procedure.
{0}
"""

_DOC_TEMPLATE_NOT_IN_PROJECT = """
Usage:
    geekcms startproject -t <template_name>

Options:
    -t <template_name> --template=<template_name>
"""

_NEWLINE = os.linesep


class DocConstructor:

    @classmethod
    def _get_explanation(cls, command, explanation):
        INDENT4 = ' ' * 4
        INDENT2 = ' ' * 2
        return (INDENT4 + command +
                INDENT2 + explanation)

    @classmethod
    def get_doc_and_cli_mapping(cls, cli_plugins):
        mapping = {}
        explanations = []
        for cli_plugin in cli_plugins:
            command, explanation = cli_plugin.get_command_and_explanation()
            explanations.append(
                cls._get_explanation(command, explanation),
            )
            mapping[command] = cli_plugin

        doc = _DOC_TEMPLATE_IN_PROJECT.format(
            _NEWLINE.join(explanations),
        )
        return doc, mapping

    @classmethod
    def get_doc_not_in_project(cls):
        return _DOC_TEMPLATE_NOT_IN_PROJECT
