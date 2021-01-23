"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import os

from setuptools import setup, find_packages

# pylint: disable=redefined-builtin

here = os.path.abspath(os.path.dirname(__file__))  # pylint: disable=invalid-name

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()  # pylint: disable=invalid-name

setup(
    name='temppathlib',
    version='1.1.0',  # don't forget to update the changelog!
    description='Wrap tempfile to give you pathlib.Path.',
    long_description=long_description,
    url='https://github.com/Parquery/temppathlib',
    author='Marko Ristin',
    author_email='marko@parquery.com',
    classifiers=[
        # yapf: disable
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        # yapf: enable
    ],
    keywords='tempfile pathlib temporary file directory mkdtemp mkstemp',
    packages=find_packages(exclude=['tests']),
    install_requires=None,
    extras_require={
        'dev': [
            # yapf: disable
            'mypy==0.790',
            'pylint==2.6.0',
            'yapf==0.20.2',
            'tox>=3,<4',
            'coverage>=5,<6',
            'pydocstyle>=5,<6',
            'twine'
            # yapf: enable
        ],
    },
    py_modules=['temppathlib'],
    package_data={"temppathlib": ["py.typed"]},
)
