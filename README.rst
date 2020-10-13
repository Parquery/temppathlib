temppathlib
===========

.. image:: https://github.com/Parquery/temppathlib/workflows/Check-push/badge.svg
    :target: https://github.com/Parquery/temppathlib/actions?query=workflow%3ACheck-push
    :alt: Check status

.. image:: https://coveralls.io/repos/github/Parquery/temppathlib/badge.svg?branch=master
    :target: https://coveralls.io/github/Parquery/temppathlib
    :alt: Test coverage

.. image:: https://badge.fury.io/py/temppathlib.svg
    :target: https://pypi.org/project/temppathlib/
    :alt: PyPI - version

.. image:: https://img.shields.io/pypi/pyversions/temppathlib.svg
    :target: https://pypi.org/project/temppathlib/
    :alt: PyPI - Python Version

Temppathlib provides wrappers around ``tempfile`` so that you can directly use them together with ``pathlib`` module.
We found it cumbersome to convert ``tempfile`` objects manually to ``pathlib.Path`` whenever we needed a temporary
file.

Additionally, we also provide:

* a context manager ``removing_tree`` that checks if a path exists and recursively deletes it
  by wrapping ``shutil.rmtree``.

* a context manager ``TmpDirIfNecessary`` that creates a temporary directory if no directory is given and otherwise
  uses a supplied directory. This is useful when you want to keep some of the temporary files for examination
  after the program finished. We usually specify an optional ``--operation_dir`` command-line argument to our programs
  and pass its value to the ``TmpDirIfNecessary``.

If you need a more complex library to transition from string paths to ``pathlib.Path``, have a look at
ruamel.std.pathlib_.

.. _ruamel.std.pathlib: https://pypi.org/project/ruamel.std.pathlib/

Usage
=====
.. code-block:: python

    import pathlib

    import temppathlib

    # create a temporary directory
    with temppathlib.TemporaryDirectory() as tmp_dir:
        tmp_pth = tmp_dir.path / "some-filename.txt"
        # do something else with tmp_dir ...

    # create a temporary file
    with temppathlib.NamedTemporaryFile() as tmp:
        # write to it
        tmp.file.write('hello'.encode())
        tmp.file.flush()

        # you can use its path.
        target_pth = pathlib.Path('/some/permanent/directory') / tmp.path.name

    # create a temporary directory only if necessary
    operation_dir = pathlib.Path("/some/operation/directory)
    with temppathlib.TmpDirIfNecessary(path=operation_dir) as op_dir:
        # do something with the operation directory
        pth = op_dir.path / "some-file.txt"

        # operation_dir is not deleted since 'path' was specified.


    with temppathlib.TmpDirIfNecessary() as op_dir:
        # do something with the operation directory
        pth = op_dir.path / "some-file.txt"

        # op_dir is deleted since 'path' argument was not specified.

    # context manager to remove the path recursively
    pth = pathlib.Path('/some/directory')
    with temppathlib.removing_tree(pth):
        # do something in the directory ...
        pass

Installation
============

* Create a virtual environment:

.. code-block:: bash

    python3 -m venv venv3

* Activate it:

.. code-block:: bash

    source venv3/bin/activate

* Install temppathlib with pip:

.. code-block:: bash

    pip3 install temppathlib

Development
===========

* Check out the repository.

* In the repository root, create the virtual environment:

.. code-block:: bash

    python3 -m venv venv3

* Activate the virtual environment:

.. code-block:: bash

    source venv3/bin/activate

* Install the development dependencies:

.. code-block:: bash

    pip3 install -e .[dev]

* We use tox for testing and packaging the distribution. Assuming that the virtual environment has been activated and
  the development dependencies have been installed, run:

.. code-block:: bash

    tox

* We also provide a set of pre-commit checks that lint and check code for formatting. Run them locally from an activated
  virtual environment with development dependencies:

.. code-block:: bash

    ./precommit.py

* The pre-commit script can also automatically format the code:

.. code-block:: bash

    ./precommit.py  --overwrite

Versioning
==========
We follow `Semantic Versioning <http://semver.org/spec/v1.0.0.html>`_. The version X.Y.Z indicates:

* X is the major version (backward-incompatible),
* Y is the minor version (backward-compatible), and
* Z is the patch version (backward-compatible bug fix).