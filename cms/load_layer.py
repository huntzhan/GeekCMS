import os


class File:

    def __init__(self, abs_path, kind):
        # be used to classify files, with each being handled by different 
        # processor(s).
        self.kind = kind
        # absolute path
        self.abs_path = abs_path
        # contents of file, the bytes having been first 
        # decoded using a platform-dependent encoding
        self.content = self._read_content()
        # in bytes
        self.size = os.path.getsize(abs_path)
        # filename(without ext), extension
        self.filename, self.extension = self._get_extension()
        # last accessed time, last modified time, created time.
        self.atime = os.path.getatime(abs_path)
        self.mtime = os.path.getmtime(abs_path)
        self.ctime = os.path.getctime(abs_path)

    def _read_content(self):
        try:
            with open(self.abs_path) as f:
                return f.read()
        except Exception as e:
            # implement it later
            raise e

    def _get_extension(self):
        root, ext = os.path.splitext(self.abs_path)
        head, filename = os.path.split(root)
        return filename, ext


class SimpleLoader:

    def __init__(self, root, exts, kind):
        # the root dir of files
        self.root = root
        # avaliable exts
        self.exts = self._read_exts(exts)
        # for marking files
        self.kind = kind

    def _read_exts(self, raw_exts):
        # transform to container
        if isinstance(raw_exts, str):
            raw_exts = [raw_exts]

        exts = []
        for ext in raw_exts:
            ext = ext if ext.startswith('.') else '.' + ext
            exts.append(ext)
        return exts

    def __call__(self, files):
        for dirpath, dirnames, filenames in os.walk(self.root):
            for name in filenames:
                # check ext
                _, ext = os.path.splitext(name)
                if ext not in self.exts:
                    continue

                # load file
                abs_path = os.path.join(dirpath, name)
                file = File(abs_path, self.kind)
                files.append(file)


def load(settings):
    files = []
    for loader in settings.loaders:
        loader(files)
    return files
