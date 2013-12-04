from process_layer import Fragment
import markdown
from .extensions.max_depth_toc import MaxDepthTocExtension
from datetime import datetime

MD_EXTENSIONS = [
    'meta',
    MaxDepthTocExtension(),
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

    exts = [
        '.md',
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
                raise e
        return meta

    def __call__(self, files, fragments):
        for file in files:
            # check markdown file
            if file.extension not in MarkdownPreprocessor.exts:
                continue
            # ok
            md = markdown.Markdown(extensions=MD_EXTENSIONS)
            html = md.convert(file.content)
            meta = self._process_meta(md.Meta)

            fragment = Fragment(html, meta, file.kind, file)
            fragments.append(fragment)
