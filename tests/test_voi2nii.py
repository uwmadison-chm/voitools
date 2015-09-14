# -*- coding: utf-8 -*-
"""
Part of the voitools package
Copyright 2015 Board of Regents of the University of Wisconsin System
Licensed under the MIT license; see LICENSE at the root of the package.

Authored by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
Imaging and Behavior.

This contains tests for the voi2nii script
"""

from __future__ import (
    print_function,
    unicode_literals,
    division,
    absolute_import)


import voitools
from voitools.scripts import voi2nii

import nibabel as nib
import numpy as np

import tempfile
import shutil
import glob
import os

import pytest


def test_voitools_runs(capsys):
    with pytest.raises(SystemExit):
        voi2nii.main(['--help'])
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert len(err) == 0


def test_filename_subs(long_data_file):
    voi_group = voitools.voi.read_file(long_data_file)
    voi = voi_group.vois[0]
    for attr in voi2nii.PATTERN_SUBS:
        pattern_str = "{{{0}}}".format(attr)
        substituted = voi2nii.make_filename(pattern_str, voi)
        assert len(substituted) > 0
        assert not pattern_str == substituted


def test_creates_files(long_data_file):
    voi_group = voitools.voi.read_file(long_data_file)
    out_dir = tempfile.mkdtemp()
    try:
        voi2nii.process_vois(
            voi_group,
            "{voi_number}.nii",
            range(voi_group.voi_count),
            out_dir)
        files = glob.glob(os.path.join(out_dir, "*"))
        assert voi_group.voi_count == len(files)
    finally:
        shutil.rmtree(out_dir)


def test_setting_affine(long_data_file, sample_nii):
    voi_group = voitools.voi.read_file(long_data_file)
    parent_nii = nib.load(sample_nii)
    voi_group.set_affine(parent_nii.get_affine())
    out_dir = tempfile.mkdtemp()
    try:
        voi2nii.process_vois(
            voi_group,
            "output.nii",
            [0],
            out_dir)
        out_nii = nib.load(os.path.join(out_dir, "output.nii"))
        assert np.array_equal(parent_nii.get_affine(), out_nii.get_affine())
    finally:
        shutil.rmtree(out_dir)
