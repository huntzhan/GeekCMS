from collections import namedtuple

from docopt import docopt

from utils import Settings
from command_layer import process_docopt_doc
from command_layer import process_args


def _init_data_set():
    attributes = [
        'files',
        'fragments',
        'products',
        'generated_paths'
    ]

    DataSet = namedtuple(
        "DataSet",
        attributes,
    )

    data_set = DataSet(
        # init with empty list
        *([] for _ in attributes)
    )
    return data_set


def default(settings):
    data_set = _init_data_set()

    for plugins in settings.classified_plugins:
        for plugin in plugins:
            plugin(data_set)


if __name__ == '__main__':
    settings = Settings()
    doc = process_docopt_doc(settings)
    args = docopt(doc, version='0.2.1')

    been_handled = process_args(settings, args)
    if not been_handled:
        default(settings)
