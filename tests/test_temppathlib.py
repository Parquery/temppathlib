#!/usr/bin/env python

# pylint: disable=missing-docstring,too-many-public-methods

import copy
import os
import pathlib
import shutil
import tempfile
import unittest
from typing import Optional  # pylint: disable=unused-import

import temppathlib


class TestRemovingTree(unittest.TestCase):
    def test_that_it_works(self) -> None:
        tmp_dir = pathlib.Path(tempfile.mkdtemp())

        try:
            pth = tmp_dir / 'oioi'
            pth.mkdir()
            with temppathlib.removing_tree(path=pth):
                self.assertTrue(pth.exists())

                subpth = pth / 'oi.txt'
                with subpth.open('wt') as fid:
                    fid.write('hey!')
                    fid.flush()

                self.assertTrue(subpth.exists())

            self.assertFalse(pth.exists())

        finally:
            if tmp_dir.exists():
                shutil.rmtree(str(tmp_dir))

    def test_no_enter(self) -> None:
        tmp_dir = pathlib.Path(tempfile.mkdtemp())

        try:
            dir1 = tmp_dir / "dir1"
            dir1.mkdir()
            dir2 = tmp_dir / "dir2"
            dir2.mkdir()

            names = sorted(list([pth.name for pth in tmp_dir.iterdir()]))
            self.assertListEqual(names, ['dir1', 'dir2'])

            # context manager invoked without enter does not delete the path.
            temppathlib.removing_tree(path=dir1)

            names = sorted(list([pth.name for pth in tmp_dir.iterdir()]))
            self.assertListEqual(names, ['dir1', 'dir2'])

            # context manager invoked with enter does delete the path.
            with temppathlib.removing_tree(path=dir1):
                pass

            names = sorted(list([pth.name for pth in tmp_dir.iterdir()]))
            self.assertListEqual(names, ['dir2'])
        finally:
            if tmp_dir.exists():
                shutil.rmtree(str(tmp_dir))


class TestTmpDirIfNecessary(unittest.TestCase):
    def test_with_path_str(self) -> None:
        basedir = pathlib.Path(tempfile.mkdtemp())

        try:
            notmp_pth = str(basedir / "no-tmp")
            with temppathlib.TmpDirIfNecessary(path=notmp_pth) as maybe_tmp_dir:
                self.assertEqual(pathlib.Path(notmp_pth), maybe_tmp_dir.path)

            self.assertTrue(os.path.exists(notmp_pth))

        finally:
            shutil.rmtree(str(basedir))

    def test_with_base_tmp_dir(self) -> None:
        basedir = pathlib.Path(tempfile.mkdtemp())

        try:
            tmp_pth = None  # type: Optional[pathlib.Path]
            with temppathlib.TmpDirIfNecessary(path=None, base_tmp_dir=basedir) as maybe_tmp_dir:
                tmp_pth = maybe_tmp_dir.path

                self.assertTrue(tmp_pth.parent == basedir)

            self.assertFalse(tmp_pth.exists())

        finally:
            shutil.rmtree(str(basedir))

    def test_prefix(self) -> None:
        with temppathlib.TmpDirIfNecessary(path=None, prefix="some_prefix") as tmp_dir:
            self.assertTrue(tmp_dir.path.name.startswith("some_prefix"))

    def test_suffix(self) -> None:
        with temppathlib.TmpDirIfNecessary(path=None, suffix="some_suffix") as tmp_dir:
            self.assertTrue(tmp_dir.path.name.endswith("some_suffix"))


class TestTemporaryDirectory(unittest.TestCase):
    def test_that_it_works(self) -> None:
        tmp_dir = pathlib.Path(tempfile.mkdtemp())

        try:
            another_tmp_dir_pth = None  # type: Optional[pathlib.Path]
            with temppathlib.TemporaryDirectory(base_tmp_dir=tmp_dir) as another_tmp_dir:
                another_tmp_dir_pth = copy.copy(another_tmp_dir.path)

                self.assertTrue(another_tmp_dir_pth.exists())

            self.assertFalse(another_tmp_dir_pth.exists())

        finally:
            if tmp_dir.exists():
                shutil.rmtree(str(tmp_dir))

    def test_with_prefix(self) -> None:
        with temppathlib.TemporaryDirectory(prefix='some-prefix') as tmp_dir:
            self.assertTrue(tmp_dir.path.name.startswith('some-prefix'))


class TestNamedTemporaryFile(unittest.TestCase):
    def test_that_it_works(self) -> None:
        pth = None  # type: Optional[pathlib.Path]
        with temppathlib.NamedTemporaryFile() as tmp:
            self.assertIsNotNone(tmp.file)
            self.assertTrue(tmp.path.exists())

            pth = tmp.path

        self.assertFalse(pth.exists())

    def test_with_dir(self) -> None:
        with temppathlib.TemporaryDirectory() as tmp_dir:
            with temppathlib.NamedTemporaryFile(dir=tmp_dir.path) as tmp:
                self.assertIsNotNone(tmp.file)
                self.assertTrue(tmp.path.exists())


class TestGettempdir(unittest.TestCase):
    def test_that_it_works(self) -> None:
        tmpdir = temppathlib.gettempdir()

        original_tmpdir = tempfile.gettempdir()
        self.assertEqual(original_tmpdir, str(tmpdir))


if __name__ == '__main__':
    unittest.main()
