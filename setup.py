#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from s3vaultlib import __application__

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = [line.strip() for line in requirements_file.readlines()]

setup_requirements = [
    'pytest-runner',
    # TODO(s3vaultlib): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name=__application__,
    version='2.3.4',
    description="Python library to expose S3 as vault to store encrypted data",
    long_description=readme + '\n\n' + history,
    author="Giuseppe Chiesa",
    author_email='mail@giuseppechiesa.it',
    url='https://github.com/gchiesa/s3vaultlib',
    packages=find_packages(include=['s3vaultlib']),
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='s3vaultlib',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    entry_points={
        'console_scripts': [
            's3vaultcli = s3vaultlib.cli:main'
        ]
    }
)
