
import os
from docopt import docopt

from .utils import (PathResolver, check_cwd_is_project)
from .doc_construct import DocConstructor
from .loadup import (SettingsProcedure, PluginProcedure)
from .protocal import (PluginRegister, BaseResource, BaseProduct, BaseMessage)


__version__ = '0.3'


def _get_args(doc, options_first=False):
    args = docopt(
        doc,
        version=__version__,
        options_first=options_first,
    )
    return args

def _not_in_project():
    doc = DocConstructor.get_doc_not_in_project()
    args = _get_args(doc)
    template = args['--template']
    if template:
        # Implement Later.
        pass
    return template


def _get_plugin_instance(plugin_index):
    plugin_cls = PluginRegister.get_plugin(plugin_index)
    return plugin_cls()


def _run_default_procedure(plugin_exec_order):
    resource_manager = BaseResource.objects
    product_manager = BaseProduct.objects
    message_manager = BaseMessage.objects
    for plugin in map(_get_plugin_instance, plugin_exec_order):
        plugin.run(
            resource_manager.values(),
            product_manager.values(),
            message_manager.values(),
        )


def _run_extended_procedure(command, cli_mapping):
    # extended procedure.
    cli_plugin = cli_mapping.get(command, None)
    if cli_plugin is None:
        print('No Such Extended Procedure: {}'.format(command))
    else:
        args = _get_args(
            cli_plugin.get_doc(),
        )
        cli_plugin.run(args)


def _in_project():
    SettingsProcedure.run()
    plugin_exec_order, cli_indices = PluginProcedure.run()

    doc, cli_mapping = DocConstructor.get_doc_and_cli_mapping(
        map(_get_plugin_instance, cli_indices),
    )
    args = _get_args(doc, options_first=True)

    # get command and decide which procedure to run.
    command = args['<command>']
    if command == 'run':
        _run_default_procedure(plugin_exec_order)
    elif command:
        _run_extended_procedure(command, cli_mapping)

    return command


def main(project_path):
    # set cwd to as project path.
    PathResolver.set_project_path(project_path)

    if not check_cwd_is_project():
        _not_in_project()
    else:
        _in_project()


if __name__ == '__main__':
    main(os.getcwd())
