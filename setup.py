#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

packages = find_packages()


def get_locals(filename):
    l = {}
    execfile(filename, {}, l)
    return l

metadata = get_locals(os.path.join('voitools', '_metadata.py'))

setup(
    name="voitools",
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['author_email'],
    license=metadata['license'],
    url=metadata['url'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'voi_info = voitools.scripts.voi_info:console',
            'voi2nii = voitools.scripts.voi2nii:console'
        ]
    }
)
