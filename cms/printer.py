import os
import shutil
from settings import OUTPUT_DIR
from settings import ARTICLE_DIR
import functools

def chain_getattr(obj, *attrs):
    try:
        result = functools.reduce(getattr, attrs, obj)    
    except:
        result = None
    finally:
        return result


class PagePrinter(object):

    def _make_related_dirs(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def _print_page(self, page, output_file_path):
        try:
            with open(output_file_path, 'w') as f:
                html = page.html
                f.write(html)
        except Exception as e:
            raise e

    def _filter_files(self, file_name_set):
        for file_name in file_name_set:
            if file_name.startswith('.') or file_name.endswith('.md'):
                continue
            yield file_name


    def _copy_relate_resource(
            self,page, article,
            input_dir_path, output_dir_path):

        input_files = set(os.listdir(input_dir_path))
        output_files = set(os.listdir(output_dir_path))
        copy_files = [file_name for file_name in self._filter_files(input_files)] 

        for name in copy_files:
            src = os.path.join(input_dir_path, name)
            dst = os.path.join(output_dir_path, name)
            shutil.copy2(src, dst)

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
            has_input = False

        # assure dirs for generating html file and resouce files.
        self._make_related_dirs(output_dir_path)
        # now, print the page.
        self._print_page(page, output_file_path)
        # copy related reosurces.
        if has_input:
            self._copy_relate_resource(
                page,
                page.article,
                input_dir_path,
                output_dir_path,
            )
