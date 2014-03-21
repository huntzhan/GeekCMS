
import os
from docopt import docopt

from .utils import (PathResolver, check_cwd_is_project)
from .doc_construct import DocConstructor
from .loadup import (SettingsProcedure, PluginProcedure)
from .protocal import (PluginRegister, BaseResource, BaseProduct, BaseMessage)


__version__ = '0.3'


def _startproject(template):
    print('Implement Later.')


def _get_plugin_instance(plugin_index):
    plugin_cls = PluginRegister.get_plugin(plugin_index)
    return plugin_cls()


def _get_args(doc, argv=None):
    args = docopt(
        doc,
        argv=argv,
        version=__version__,
        options_first=True,
    )
    return args

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


def main(project_path):
    # set cwd to as project path.
    PathResolver.set_project_path(project_path)

    if not check_cwd_is_project():
        # not in project.
        doc = DocConstructor.get_doc_not_in_project()
        args = _get_args(doc)
        template = args['--template']
        if template:
            _startproject(template)
    else:
        # in project.
        SettingsProcedure.run()
        plugin_exec_order, cli_indices = PluginProcedure.run()

        doc, cli_mapping = DocConstructor.get_doc_and_cli_mapping(
            map(_get_plugin_instance, cli_indices),
        )
        args = _get_args(doc)

        # get command and decide which procedure to run.
        command = args['<command>']
        if command == 'run':
            # default procedure.
            _run_default_procedure(plugin_exec_order)
        else:
            # extended procedure.
            argv = [command] + args['<args>']
            cli_plugin = cli_mapping.get(command, None)
            if cli_plugin is None:
                print('No Such Extended Procedure: {}'.format(command))
            else:
                args = _get_args(
                    cli_plugin.get_doc(),
                    argv,
                )
                cli_plugin.run(args)


if __name__ == '__main__':
    main(os.getcwd())
