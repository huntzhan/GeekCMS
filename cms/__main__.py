from collections import namedtuple

from docopt import docopt

from utils import Settings
from command_layer import process_docopt_doc
from command_layer import process_args


def default(settings):
    data_set = namedtuple(
        "DataSet",
        ['files', ''],
    )

    for plugins in settings.classified_plugins:
        for plugin in plugins:
            plugin(data_set)


if __name__ == '__main__':
    settings = Settings()
    doc = process_docopt_doc(settings)
    args = docopt(doc, version='0.2.1')

    if process_args(settings, args):
        default(settings)
