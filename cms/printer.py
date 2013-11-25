import os
import shutil
from settings import OUTPUT_DIR
from settings import ARTICLE_DIR
import functools
import collections

def chain_getattr(obj, *attrs):
    try:
        result = functools.reduce(getattr, attrs, obj)    
    except:
        result = None
    finally:
        return result


class PagePreprocessor(object):


    def _make_related_dirs(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def _filter_file_name(self, file_name):
        if file_name.startswith('.') or file_name.endswith('.md'):
            return False
        else:
            return True

    def _judge_copy(self, src_file_path, dst_file_path):

        # src file might not exist.
        try:
            src_mtime = os.path.getmtime(src_file_path)
        except TypeError:
            return True

        # dst file might not exsit.
        try:
            dst_mtime = os.path.getmtime(dst_file_path)
        except OSError:
            return True
        
        # both exsit.
        # judge by last modified time.
        if src_mtime > dst_mtime:
            return True
        else:
            return False

    def _generate_file_set_for_copy(
            self, page, article,
            input_dir_path, output_dir_path):

        # filter input file names 
        input_file_names = filter(
            self._filter_file_name, os.listdir(input_dir_path),
        )
        # filtering output file names is not necessary
        output_file_names = os.listdir(output_dir_path)

        path_pairs = []
        # generate list of files will be copied.
        for name in input_file_names:
            src_file_path = os.path.join(input_dir_path, name)
            dst_file_path = os.path.join(output_dir_path, name)

            if self._judge_copy(src_file_path, dst_file_path):
                path_pairs.append(
                    (src_file_path, dst_file_path),
                )
        return path_pairs


    def __call__(self, page, input, output, resource_copier):
        # assure dirs for generating html file and resouce files.
        self._make_related_dirs(output.dir_path)

        # page
        if self._judge_copy(input.file_path, output.file_path):
            page.active = True
        else:
            page.active = False
        # resource
        if input.has_input:
            path_pairs = self._generate_file_set_for_copy(
                page,
                page.article,
                input.dir_path,
                output.dir_path,
            )
            resource_copier.update_path_pairs(path_pairs)


class IOPathTranslator(object):

    Input = collections.namedtuple(
        'Input',
        ['has_input', 'file_path', 'dir_path'],
    )
    Output = collections.namedtuple(
        'Output',
        ['file_path', 'dir_path'],
    )

    def _get_file_path_and_dir_path(self, root_path, relative_path):
        file_path = os.path.join(root_path, relative_path)
        dir_path, file_name = os.path.split(file_path)
        return file_path, dir_path

    def __call__(self, page):
        # output
        output_file_path, output_dir_path = self._get_file_path_and_dir_path(
            OUTPUT_DIR, page.url.lstrip('/'),
        )
        # input
        # page might not have a input file
        try: 
            input_file_path, input_dir_path = self._get_file_path_and_dir_path(
                ARTICLE_DIR, chain_getattr(page, 'article', 'relative_path'),
            )
            has_input = True
        except:
            input_file_path = None
            input_dir_path = None
            has_input = False

        input = self.Input(has_input, input_file_path, input_dir_path)
        output = self.Output(output_file_path, output_dir_path)
        return input, output


class PagePrinter(object):

    def _print_page(self, page, output_file_path):
        try:
            with open(output_file_path, 'w') as f:
                html = page.html
                f.write(html)
        except Exception as e:
            raise e

    def __call__(self, page, output_file_path):
        if page.active:
            self._print_page(page, output_file_path)


class PageRelatedResourceCopier(object):

    def __init__(self):
        self._path_pairs = []

    def update_path_pairs(self, path_pairs):
        self._path_pairs.extend(path_pairs)

    def copy(self):
        # remove duplicated pairs
        path_pairs = set(self._path_pairs)
        for src, dst in path_pairs:
            shutil.copy2(src, dst)

class PageSetProcessor(object):

    _io_path_translator = IOPathTranslator()
    _preprocessor = PagePreprocessor()
    _printer = PagePrinter()

    def _process_page(self, page):
        input, output = self._io_path_translator(page)
        self._preprocessor(page, input, output, self._resource_copier)
        self._printer(page, output.file_path)

    def __call__(self, page_set):
        self._resource_copier = PageRelatedResourceCopier()
        for page in page_set:
            self._process_page(page)
        self._resource_copier.copy()
