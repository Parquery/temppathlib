"""Wrap tempfile to give you pathlib.Path."""

import pathlib
import shutil
import tempfile
from typing import IO, Any, Optional, Union  # pylint: disable=unused-import


class removing_tree:  # pylint: disable=invalid-name
    """Check if the path exists, and if it does, calls shutil.rmtree on it."""

    def __init__(self, path: Union[str, pathlib.Path]) -> None:
        """Initialize with the given value."""
        if isinstance(path, str):
            self.path = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            self.path = path
        else:
            raise ValueError("Unexpected type of 'path': {}".format(type(path)))

    def __enter__(self) -> pathlib.Path:
        """Give back the path that will be removed."""
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Remove the path if it exists."""
        if self.path.exists():
            shutil.rmtree(str(self.path))


class TmpDirIfNecessary:
    """
    Forward the directory path (if defined) or create a temporary directory.

    If dont_delete_tmp_dir is set to True, the temporary directory is not deleted on exit.

    The directory (be it a temporary or not) is created on enter. If the path was not specified (and a temporary
    directory needs to be created), its name is generated only on enter.
    """

    def __init__(self,
                 path: Union[None, str, pathlib.Path],
                 base_tmp_dir: Union[None, str, pathlib.Path] = None,
                 dont_delete_tmp_dir: bool = False) -> None:
        """
        Initialize with the given values.

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

        self._path = None  # type: Optional[pathlib.Path]

        if path is None:
            pass
        elif isinstance(path, str):
            self._path = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            self._path = path
        else:
            raise ValueError("Unexpected type for the argument `path`: {}".format(type(path)))

        self.dont_delete = dont_delete_tmp_dir

        self.__use_tmp_dir = path is None

        self.exited = False

    @property
    def path(self) -> pathlib.Path:
        """Get the underlying path or raise if the path has not been set."""
        if self._path is None:
            raise RuntimeError("The _path has not been set. "
                               "Are you using {} outside of the context management?".format(self.__class__.__name__))

        return self._path

    def __enter__(self) -> 'TmpDirIfNecessary':
        """Create the temporary directory if necessary."""
        if self.exited:
            raise RuntimeError("Already exited")

        if self._path is None:
            if self.base_tmp_dir is None:
                self._path = pathlib.Path(tempfile.mkdtemp())
            else:
                self._path = pathlib.Path(tempfile.mkdtemp(dir=str(self.base_tmp_dir)))
        else:
            self._path.mkdir(exist_ok=True, parents=True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        """Remove the directory if dont_delete has not been set."""
        if self.__use_tmp_dir and not self.dont_delete:
            shutil.rmtree(str(self._path))


class TemporaryDirectory:
    """
    Create a temporary directory and deletes it on exit.

    The path to the temporary directory is generated and the directory is created only on __enter__.
    """

    def __init__(self,
                 base_tmp_dir: Union[None, str, pathlib.Path] = None,
                 prefix: Optional[str] = None,
                 dont_delete: bool = False) -> None:
        """
        Initialize with the given values.

        :param base_tmp_dir: if specified, this directory will be used as the parent of the temporary directory.
        :param prefix: if specified, the prefix of the directory name
        :param dont_delete: if set, the directory is not deleted upon close().
        """
        self.exited = False
        self._path = None  # type: Optional[pathlib.Path]

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

    def __enter__(self) -> 'TemporaryDirectory':
        """Create the temporary directory."""
        if self.exited:
            raise RuntimeError("Already exited")

        base_tmp_dir = str(self.base_tmp_dir) if self.base_tmp_dir is not None else None
        self._path = pathlib.Path(tempfile.mkdtemp(prefix=self.prefix, dir=base_tmp_dir))

        return self

    @property
    def path(self) -> pathlib.Path:
        """Get the underlying path or raise if the path has not been set."""
        if self._path is None:
            raise RuntimeError("The _path has not been set. "
                               "Are you using {} outside of the context management?".format(self.__class__.__name__))

        return self._path

    def close(self) -> None:
        """
        Close the temporary directory.

        If already closed, does nothing. If dont_delete not set, deletes the temporary directory if it exists.

        """
        if not self.exited:
            if not self.dont_delete and self._path is not None and self._path.exists():
                shutil.rmtree(str(self._path))

            self.exited = True

    def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        """Close the temporary directory upon exit."""
        self.close()


class NamedTemporaryFile:
    """Wrap tempfile.NamedTemporaryFile with pathlib.Path."""

    def __init__(
            self,
            mode: str = 'w+b',
            buffering: int = -1,
            encoding: Optional[str] = None,
            newline: Optional[str] = None,
            suffix: Optional[str] = None,
            prefix: Optional[str] = None,
            dir: Optional[pathlib.Path] = None,  # pylint: disable=redefined-builtin
            delete: bool = True) -> None:
        """
        Initialize with the given values.

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
            dir=str(dir) if dir is not None else None,
            delete=delete)

        self.path = pathlib.Path(self.__tmpfile.name)

        file = self.__tmpfile.file  # type: ignore
        self.file = file  # type: IO[Any]
        self.delete = delete

    def close(self) -> None:
        """Forward close request to the underlying temporary file."""
        self.__tmpfile.close()

    def __enter__(self) -> 'NamedTemporaryFile':
        """Return this object; no further action is performed."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Close the temporary file."""
        self.close()


def gettempdir() -> pathlib.Path:
    """
    Wrap ``tempfile.gettempdir``.

    Please see the documentation of ``tempfile.gettempdir`` for more details:
    https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir
    """
    return pathlib.Path(tempfile.gettempdir())
