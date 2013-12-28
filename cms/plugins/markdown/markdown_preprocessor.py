from datetime import datetime
import markdown
from process_layer import Fragment
from .extensions.max_depth_toc import MaxDepthTocExtension
from .extensions.syntax_highlighter import SyntaxHighlighterExtension


MD_EXTENSIONS = [
    'meta',
    MaxDepthTocExtension(),
    SyntaxHighlighterExtension(),
]


def article_activeness(x):
    if x[0].lower() == 'false':
        return False
    else:
        return True


meta_processor = [
    ('title', 'title', lambda x: x[0]),
    ('date', 'post_time', lambda x: datetime.strptime(x[0], '%d/%m/%Y')),
    ('activeness', 'active', article_activeness),
]


class MarkdownPreprocessor:

    # avaliable markdown extentions
    exts = [
        '.markdown',
        '.mdown',
        '.mkdn',
        '.md',
        '.mkd',
        '.mdwn',
        '.mdtxt',
        '.mdtext',
    ]

    def _process_meta(self, raw_meta):
        meta = {}
        for key, cls_attr, processor in meta_processor:
            try:
                data = raw_meta.get(key, None)
                if data is None:
                    continue
                val = processor(data)
                meta[cls_attr] = val
            except Exception as e:
                # implemented later
                raise e
        return meta

    def __call__(self, data_set):
        for file in data_set.files:
            # check markdown file
            if file.extension not in MarkdownPreprocessor.exts:
                continue
            # ok
            md = markdown.Markdown(extensions=MD_EXTENSIONS)
            html = md.convert(file.data)
            meta = self._process_meta(md.Meta)

            fragment = Fragment(file.mark, html)
            # add meta attribute
            fragment.meta = meta
            # make one-to-one connection
            fragment.file = file
            data_set.fragments.append(fragment)
