from docopt import docopt

from utils import Settings
from load_layer import load
from process_layer import preprocess
from process_layer import process
from write_layer import write
from command_layer import process_docopt_doc
from command_layer import process_args


def default(settings):
    files = load(settings)
    fragments = preprocess(settings, files)
    pages = process(settings, fragments)
    write(settings, pages)


if __name__ == '__main__':
    settings = Settings()
    doc = process_docopt_doc(settings)
    args = docopt(doc, version='0.2.1')

    if process_args(settings, args):
        default(settings)
