import os
import shutil
from settings import OUTPUT_DIR
from settings import ARTICLE_DIR


class PagePrinter(object):

    def __call__(self, page):

        def make_related_dirs(page, path):
            head, tail = os.path.split(path)
            if not os.path.exists(head):
                os.makedirs(head)

        def print_page(page, path):
            try:
                with open(path, 'w') as f:
                    html = page.html
                    f.write(html)
            except Exception as e:
                raise e

        def copy_relate_resource(page, path):
            article = getattr(page, 'article', None)
            if article is None:
                return

            from_path = os.path.join(ARTICLE_DIR, article.relative_path)
            head, tail = os.path.split(from_path)
            from_path = head

            head, tail = os.path.split(path)
            to_path = head

            from_files = set(os.listdir(from_path))
            to_files = set(os.listdir(to_path))
            copy_files = from_files - to_files

            for name in copy_files:
                if name.startswith('.') or name.endswith('.md'):
                    continue
                src = os.path.join(from_path, name)
                dst = os.path.join(to_path, name)
                shutil.copy2(src, dst)

        path = os.path.join(OUTPUT_DIR, page.url.lstrip('/'))
        
        make_related_dirs(page, path)
        print_page(page, path)
        copy_relate_resource(page, path)
