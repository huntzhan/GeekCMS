import os
import shutil
import collections

from utils import url2rel_path
from load_layer import VIRTUAL_FILE

from .settings import OUTPUT_DIR
from .settings import ARTICLE
from .settings import ABOUT
from .settings import HOME
from .settings import ARCHIVE


class IOPathTranslator:

    Input = collections.namedtuple(
        'Input',
        ['has_input', 'file_path', 'dir_path'],
    )
    Output = collections.namedtuple(
        'Output',
        ['file_path', 'dir_path'],
    )

    def _get_file_path_and_dir_path(self, root, rel_path):
        file_path = os.path.join(root, rel_path)
        dir_path, file_name = os.path.split(file_path)
        return file_path, dir_path

    def __call__(self, page):
        # output
        output_file_path, output_dir_path = self._get_file_path_and_dir_path(
            OUTPUT_DIR, url2rel_path(page.url)
        )
        # input
        # page might not have a input file
        try:
            file = page.fragment.file
            input_file_path, input_dir_path = self._get_file_path_and_dir_path(
                '', file.abs_path,
            )
            has_input = True
        except:
            input_file_path = None
            input_dir_path = None
            has_input = False

        input = self.Input(has_input, input_file_path, input_dir_path)
        output = self.Output(output_file_path, output_dir_path)
        return input, output


class PageWriter:

    def _print_page(self, page, output_file_path):
        try:
            with open(output_file_path, 'w') as f:
                html = page.data
                f.write(html)
        except Exception as e:
            raise e

    def __call__(self, page, output_file_path):
        #if page.can_generate:
        self._print_page(page, output_file_path)


class SimpleWriter:

    def __init__(self):
        self._io_path_translator = IOPathTranslator()
        self._writer = PageWriter()

    def __call__(self, data_set):

        for product in data_set.products:
            if product.mark not in [ARTICLE, ABOUT, HOME, ARCHIVE]:
                continue
            # html page
            input, output = self._io_path_translator(product)
            self._writer(product, output.file_path)

        for file in data_set.files:
            if file.mark != VIRTUAL_FILE:
                continue
            # resource file
            output_path = os.path.join(
                OUTPUT_DIR, file.filename + file.extension
            )
            file.copy_to(output_path)
