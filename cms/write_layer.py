import os


class SimpleWriter:

    def __init__(self, output_path):
        self.output_path = output_path

    def _write_page(self, page):
        output_file_path = url2abs_path(self.output_path, page.url)
        try:
            with open(output_file_path, 'w') as f:
                html = page.html
                f.write(html)
        except Exception as e:
            raise e
        return output_file_path

    def __call__(self, pages, paths):
        for page in pages:
            path = self._write_page(page)
            paths.append(path)


def write(settings, pages):
    paths = []
    for writer in settings.writers:
        writer(pages, paths)
