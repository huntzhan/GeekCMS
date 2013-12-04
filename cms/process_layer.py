class Fragment:
    """
    HTML fragment.
    """
    def __init__(self, html, meta, kind, file=None):
        self.html = html
        self.meta = meta
        self.kind = kind
        self.file = file


class Page:

    def __init__(self, html, url, kind, fragment=None):
        self.html = html
        self.url = url
        self.kind = kind
        self.fragment = fragment


def preprocess(settings, files):
    fragments = []
    for preprocessor in settings.preprocessors:
        preprocessor(files, fragments)
    return fragments


def process(settings, fragments):
    pages = []
    for processor in settings.processors:
        processor(fragments, pages)
    return pages
