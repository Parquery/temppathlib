""" wraps tempfile to give you pathlib.Path. """

import pathlib
import shutil
import tempfile
from typing import Union, Optional, IO, Any  # pylint: disable=unused-import


class removing_tree:  # pylint: disable=invalid-name
    """
    checks if the path exists, and if it does, calls shutil.rmtree on it.
    """

    def __init__(self, path: Union[str, pathlib.Path]) -> None:
        if isinstance(path, str):
            self.path = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            self.path = path
        else:
            raise ValueError("Unexpected type of 'path': {}".format(type(path)))

    def __enter__(self) -> pathlib.Path:
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.path.exists():
            shutil.rmtree(str(self.path))


class TmpDirIfNecessary:
    """
    either forwards the directory path (if defined) or creates a temporary directory and deletes it on exit
    if dont_delete_tmp_dir is False.

    The directory (be it a temporary or not) is created on enter. If the path was not specified (and a temporary
    directory needs to be created), its name is generated only on enter.
    """

    def __init__(self,
                 path: Union[None, str, pathlib.Path],
                 base_tmp_dir: Union[None, str, pathlib.Path] = None,
                 dont_delete_tmp_dir: bool = False) -> None:
        """
        :param path: provided path to the directory; if specified, no temporary directory is created.
        :param base_tmp_dir: parent directory of the temporary directories; if not set,
        the default is used (usually '/tmp'). This path is only used if a temporary directory needs to be created
        and has no effect if 'path' was provided.

        :param dont_delete_tmp_dir: if set, the temporary directory is not deleted upon close.

        If the 'path' was provided, this argument has no effect.
        """
        if base_tmp_dir is None:
            self.base_tmp_dir = base_tmp_dir
        elif isinstance(base_tmp_dir, pathlib.Path):
            self.base_tmp_dir = base_tmp_dir
        elif isinstance(base_tmp_dir, str):
            self.base_tmp_dir = pathlib.Path(base_tmp_dir)
        else:
            raise ValueError("Unexpected type of 'base_tmp_dir': {}".format(type(base_tmp_dir)))

        self.path = None  # type: Optional[pathlib.Path]

        if path is None:
            pass
        elif isinstance(path, str):
            self.path = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            self.path = path
        else:
            raise ValueError("Unexpected type for the argument `path`: {}".format(type(path)))

        self.dont_delete = dont_delete_tmp_dir

        self.__use_tmp_dir = path is None

        self.exited = False

    def __enter__(self):
        if self.exited:
            raise RuntimeError("Already exited")

        if self.path is None:
            if self.base_tmp_dir is None:
                self.path = pathlib.Path(tempfile.mkdtemp())
            else:
                self.path = pathlib.Path(tempfile.mkdtemp(dir=str(self.base_tmp_dir)))
        else:
            self.path.mkdir(exist_ok=True, parents=True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__use_tmp_dir and not self.dont_delete:
            shutil.rmtree(str(self.path))


class TemporaryDirectory:
    """
    creates a temporary directory and deletes it on exit.

    The path to the temporary directory is generated and the directory is created only on __enter__.
    """

    def __init__(self,
                 base_tmp_dir: Union[None, str, pathlib.Path] = None,
                 prefix: Optional[str] = None,
                 dont_delete: bool = False) -> None:
        """
        :param base_tmp_dir: if specified, this directory will be used as the parent of the temporary directory.
        :param prefix: if specified, the prefix of the directory name
        :param dont_delete: if set, the directory is not deleted upon close().
        """
        self.exited = False
        self.path = None  # type: Optional[pathlib.Path]

        if base_tmp_dir is None:
            self.base_tmp_dir = base_tmp_dir
        elif isinstance(base_tmp_dir, pathlib.Path):
            self.base_tmp_dir = base_tmp_dir
        elif isinstance(base_tmp_dir, str):
            self.base_tmp_dir = pathlib.Path(base_tmp_dir)
        else:
            raise ValueError("Unexpected type of 'base_tmp_dir': {}".format(type(base_tmp_dir)))

        self.prefix = prefix
        self.dont_delete = dont_delete

    def __enter__(self):
        if self.exited:
            raise RuntimeError("Already exited")

        base_tmp_dir = self.base_tmp_dir.as_posix() if self.base_tmp_dir is not None else None
        self.path = pathlib.Path(tempfile.mkdtemp(prefix=self.prefix, dir=base_tmp_dir))

        return self

    def close(self) -> None:
        """
        closes the temporary directory.

        If already closed, does nothing. If dont_delete not set, deletes the temporary directory if it exists.

        :return:
        """
        if not self.exited:
            if not self.dont_delete and self.path is not None and self.path.exists():
                shutil.rmtree(str(self.path))

            self.exited = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class NamedTemporaryFile:
    """
    wraps tempfile.NamedTemporaryFile with pathlib.Path.
    """

    def __init__(
            self,
            mode='w+b',
            buffering: int = -1,
            encoding: Optional[str] = None,
            newline=None,
            suffix: Optional[str] = None,
            prefix: Optional[str] = None,
            dir: Optional[pathlib.Path] = None,  # pylint: disable=redefined-builtin
            delete: bool = True) -> None:
        """
        The description of parameters is copied from the tempfile.NamedTemporaryFile docstring.

        :param mode: the mode argument to io.open (default "w+b")
        :param buffering: the buffer size argument to io.open (default -1).
        :param encoding: the encoding argument to io.open (default None)
        :param newline: the newline argument to io.open (default None)
        :param suffix: If 'suffix' is not None, the file name will end with that suffix,
        otherwise there will be no suffix.

        :param prefix: If 'prefix' is not None, the file name will begin with that prefix,
        otherwise a default prefix is used.

        :param dir: If 'dir' is not None, the file will be created in that directory,
        otherwise a default directory is used.

        :param delete: whether the file is deleted on close (default True).
        """
        # pylint: disable=too-many-arguments
        self.__tmpfile = tempfile.NamedTemporaryFile(
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            newline=newline,
            suffix=suffix,
            prefix=prefix,
            dir=dir.as_posix() if dir is not None else None,
            delete=delete)

        self.path = pathlib.Path(self.__tmpfile.name)

        file = self.__tmpfile.file  # type: ignore
        self.file = file  # type: IO[Any]
        self.delete = delete

    def close(self) -> None:
        """ forwards close() to the underlying temporary file. """
        self.__tmpfile.close()

    def __enter__(self) -> 'NamedTemporaryFile':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
