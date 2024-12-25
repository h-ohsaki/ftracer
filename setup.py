#!/usr/bin/env python3

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="ftracer",
    version="1.4",
    author="Hiroyuki Ohsaki",
    author_email="ohsaki@lsnl.jp",
    description=
    "Decorator functions to trace invocation of functions and class methods.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/h-ohsaki/ftracer",
    packages=setuptools.find_packages(),
    install_requires=[''],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
