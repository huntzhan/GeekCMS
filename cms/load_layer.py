import os
import shutil
import operator
from utils import BaseData


VIRTUAL_FILE = 'virtual_file'


class _AttributeMixin:

    def _extract_attributes(self, abs_path):
        # absolute path
        self.abs_path = abs_path
        # in bytes
        self.size = os.path.getsize(abs_path)
        # filename(without ext), extension
        self.filename, self.extension = self._get_extension(abs_path)
        # last accessed time, last modified time, created time.
        self.atime = os.path.getatime(abs_path)
        self.mtime = os.path.getmtime(abs_path)
        self.ctime = os.path.getctime(abs_path)

    def _get_extension(self, abs_path):
        root, ext = os.path.splitext(abs_path)
        head, filename = os.path.split(root)
        return filename, ext


class ContentFile(BaseData, _AttributeMixin):
    """
    ContentFile must handle a file with data.
    """
    def __init__(self, abs_path, mark, *args, **kwargs):
        super().__init__(
            mark,
            # contents of file, the bytes having been first
            # decoded using a platform-dependent encoding
            self._read_content(abs_path),
        )

        self._extract_attributes(abs_path)

    def _read_content(self, abs_path):
        try:
            with open(abs_path) as f:
                return f.read()
        except Exception as e:
            # implement it later
            raise e


class VirtualFile(BaseData, _AttributeMixin):
    """
    Unlike ContentFile, VirtualFile do not read the content into
    memory. This class is mainly implemented for copying the resource
    file.
    """
    def __init__(self, abs_path, *args, **kwargs):
        super().__init__(
            VIRTUAL_FILE,
            None,
        )
        self._extract_attributes(abs_path)

    def copy_to(self, path):
        shutil.copy2(self.abs_path, path)

    @property
    def binary_data(self):
        with open(self.abs_path, 'rb') as f:
            data = f.read()
        return data


class _BaseLoader:
    """
    Base class of various Loaders.
    """
    def __init__(self, dir_path, exts, mark, file_cls,
                 exts_exclude=False):
        # root of files to be loaded.
        assert os.path.isdir(dir_path)
        self.dir_path = dir_path
        # avaliable exts
        self.exts = self._read_exts(exts)
        # for marking files
        self.mark = mark
        # class to initiate file
        self.file_cls = file_cls
        # exclusion mode
        self.exts_exclude = exts_exclude

    def _read_exts(self, raw_exts):
        # transform to container
        if isinstance(raw_exts, str):
            raw_exts = [raw_exts]

        exts = []
        for ext in raw_exts:
            # ensure ext starts with '.'
            ext = ext if ext.startswith('.') else '.' + ext
            exts.append(ext)
        return exts

    def _check_ext(self, file_name):
        _, ext = os.path.splitext(file_name)

        return operator.xor(
            ext in self.exts,
            self.exts_exclude,
        )


    def __call__(self, data_set):
        # search all descendants of self.dir_path
        for dirpath, dirnames, filenames in os.walk(self.dir_path):
            for name in filenames:
                # check ext
                if not self._check_ext(name):
                    continue

                # load file
                abs_path = os.path.join(dirpath, name)
                try:
                    file = self.file_cls(abs_path, self.mark)
                except:
                    continue
                data_set.files.append(file)


class ContentFileLoader(_BaseLoader):
    def __init__(self, dir_path, exts, mark):
        super().__init__(dir_path, exts, mark, ContentFile)


class VirtualFileLoader(_BaseLoader):
    def __init__(self, dir_path, exts, exts_exclude=True):
        super().__init__(
            dir_path,
            exts,
            VIRTUAL_FILE,
            VirtualFile,
            exts_exclude,
        )
