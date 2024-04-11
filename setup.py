#!/usr/bin/env python3
"""Srp Energy setup script."""
import os
from datetime import datetime as dt
from setuptools import setup, find_packages
import bermuda.const as berm_const


def read(fname):
    """Read README.rst into long_description.

    ``long_description`` is what ends up on the PyPI front page.
    """
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        contents = f.read()

    return contents


PROJECT_NAME = 'Bermuda Growing Days'
PROJECT_PACKAGE_NAME = 'bermuda'
PROJECT_LICENSE = 'Apache License 2.0'
PROJECT_AUTHOR = 'The Bermuda Authors'
PROJECT_COPYRIGHT = ' 2019-{}, {}'.format(dt.now().year, PROJECT_AUTHOR)

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

REQUIRES = [
    'paho-mqtt>=1.4.0',
    'python-forecastio>=1.4.0',
    'PyYAML>=5.1'
]

MIN_PY_VERSION = '.'.join(map(str, berm_const.REQUIRED_PYTHON_VER))

setup(
    name=PROJECT_PACKAGE_NAME,
    version=berm_const.__version__,
    author=PROJECT_AUTHOR,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    python_requires='>={}'.format(MIN_PY_VERSION),
    test_suite='tests',
    description=(
        "Publish the number of days that are warm enough for bermuda to grow"),
    long_description=read('README.rst'),
    license=PROJECT_LICENSE,
    entry_points={
        'console_scripts': [
            'berm = bermuda.app:main'
        ]
    },
)
