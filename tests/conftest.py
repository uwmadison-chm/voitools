"""
Part of the voitools package
Copyright 2015 Board of Regents of the University of Wisconsin System
Licensed under the MIT license; see LICENSE at the root of the package.

Authored by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
Imaging and Behavior.

This contains fixtures for the test suite.
"""

import pytest
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture
def long_data_filename():
    return os.path.join(DATA_DIR, "long.voi")


@pytest.yield_fixture
def long_data_file(long_data_filename):
    with open(long_data_filename, "r") as f:
        yield f


@pytest.fixture
def triple_data_filename():
    return os.path.join(DATA_DIR, "triples.voi")


@pytest.yield_fixture
def triple_data_file(triple_data_filename):
    with open(triple_data_filename, "r") as f:
        yield f

@pytest.fixture
def sample_nii():
    return os.path.join(DATA_DIR, "sample.nii.gz")
