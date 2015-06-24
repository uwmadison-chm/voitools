# -*- coding: utf-8 -*-
"""
Part of the voitools package
Copyright 2015 Board of Regents of the University of Wisconsin System
Licensed under the MIT license; see LICENSE at the root of the package.

Authored by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
Imaging and Behavior.

This contains tests for voitools.voi
"""

from __future__ import (
    print_function,
    unicode_literals,
    division,
    absolute_import)

from voitools import voi
import os
import logging

import pytest

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

voi.logger.setLevel(logging.DEBUG)


@pytest.fixture
def long_data_filename():
    return os.path.join(DATA_DIR, "long.voi")


@pytest.yield_fixture
def long_data_file(long_data_filename):
    with open(long_data_filename, "r") as f:
        yield f


@pytest.yield_fixture
def triple_data_file():
    with open(os.path.join(DATA_DIR, "triples.voi"), "r") as f:
        yield f


def test_read_group_header(long_data_file):
    voi_group = voi.VOIGroup.from_io(long_data_file)
    assert len(voi_group.header.keys()) > 0
    assert voi_group.voi_count == 3


def test_byte_order(long_data_file):
    voi_group = voi.VOIGroup.from_io(long_data_file)
    assert voi_group.data_type_string == ">i4"


def test_read_data_long(long_data_file):
    voi_group = voi.VOIGroup.from_io(long_data_file)
    voi_0 = voi.VOI.from_io(voi_group, long_data_file)
    assert len(voi_0.voxel_indexes) == voi_0.voxel_count
    assert min(voi_0.voxel_indexes) > 0


def test_read_data_triples(triple_data_file):
    voi_group = voi.VOIGroup.from_io(triple_data_file)
    voi_0 = voi.VOI.from_io(voi_group, triple_data_file)
    assert len(voi_0.voxel_indexes) == voi_0.voxel_count
    assert min(voi_0.voxel_indexes) > 0
    # Computed by hand.
    assert voi_0.voxel_indexes[0] == 2182291


def test_voi_properties(long_data_file):
    voi_group = voi.VOIGroup.from_io(long_data_file)
    voi_0 = voi.VOI.from_io(voi_group, long_data_file)
    assert voi_0.name == "caudate L"
    assert voi_0.shape == voi.Triple(79, 95, 68)
    assert voi_0.voxel_dimensions == voi.Triple(2.0, 2.0, 2.0)


def test_read_file_filename(long_data_filename):
    voi_group = voi.read_file(long_data_filename)
    assert voi_group.voi_count == len(voi_group.vois)


#def test_read_file_io(long_data_file):
#    voi_group = voi.read_file(long_data_file)
#    assert voi_group.voi_count == len(voi_group.vois)