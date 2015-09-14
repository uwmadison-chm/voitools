#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of the voitools package
# Copyright 2015 Board of Regents of the University of Wisconsin System
# Licensed under the MIT license; see LICENSE at the root of the package.

# Authored by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
# Imaging and Behavior.

"""Convert a spamalize .voi file into a set of nifti files.

This program will produce one .nii file per VOI in a VOI group (.voi) file;
the name will be determined by the --pattern parameter.

Usage:
  voi2nii [options] <datafile>
  voi2nii -h | --help

Options:
  --pattern=<pat>       How to name the output. Surround fields in {}.
                        Available fields:
                        base_name   The name of the file the VOI group is
                                    based on
                        cur_name    The current name of the VOI group file
                        voi_number  The index of this VOI
                        voxel_count The number of voxels in the VOI
                        voi_name    The name of this VOI
                        [default: {cur_name}-{voi_name}-{voi_number}.nii]
  --voi-numbers=<nums>  The indexes (starting from 1) of the VOIs to convert.
                        Separate with commas. If not specified, converts all
                        VOIs.
  --affine-parent=<parent_file>
                        Read orientation, origin, and voxel size from this
                        file.
                        If not specified, reads voxel size from the .voi file
                        and assumes a centered origin in RPI orientation.
  --out-dir=<dir>       Directory to write the output files [default: .]
  -h --help             Show this screen
  --version             Show version
  -v --verbose          Display debugging information
"""

import sys
import logging
import re
import os

import nibabel as nib

import voitools
from voitools import voi
from voitools.vendor import docopt

logger = voi.logger

PATTERN_SUBS = set(
    ['base_name', 'cur_name', 'voi_number', 'voxel_count', 'voi_name'])
WORD_CHAR_RE = re.compile(r"\W+")


def main(argv):
    arguments = docopt.docopt(
        __doc__,
        argv,
        version="voitools {0}".format(voitools.__version__))
    logger.setLevel(logging.INFO)
    if arguments['--verbose']:
        logger.setLevel(logging.DEBUG)
    logger.debug(arguments)
    voi_group = voitools.voi.read_file(arguments['<datafile>'])
    voi_indexes = make_voi_numbers(voi_group, arguments['--voi-numbers'])
    voi_group.set_affine(make_affine(arguments['--affine-parent']))
    process_vois(
        voi_group,
        arguments['--pattern'],
        voi_indexes,
        arguments['--out-dir'])


def make_voi_numbers(voi_group, voi_numbers_string):
    if voi_numbers_string is None:
        return range(voi_group.voi_count)
    return [int(num) - 1 for num in voi_numbers_string.split(",")]


def make_affine(affine_parent_name):
    if affine_parent_name is None:
        return None
    return nib.load(affine_parent_name).get_affine()


def make_filename(pattern, voi):
    out_name = pattern
    for attr in PATTERN_SUBS:
        val = getattr(voi, "{0}".format(attr))
        val_safe = re.sub(WORD_CHAR_RE, "_", str(val))
        out_name = out_name.replace(
            "{{{0}}}".format(attr), str(val_safe))
    return out_name


def process_vois(voi_group, name_pattern, voi_indexes, out_dir):
    vois = [voi_group.vois[i] for i in voi_indexes]
    for cur_voi in vois:
        logger.debug("Converting VOI {0}".format(cur_voi.voi_number))
        nii = make_nifti(cur_voi)
        out_filename = os.path.join(
            out_dir, make_filename(name_pattern, cur_voi))
        nii.to_filename(out_filename)


def make_nifti(cur_voi):
    # It's OK if this is None, we'll just choose a centered affine.
    logger.debug("Making nifti for {0}".format(cur_voi.voi_number))
    img = nib.Nifti1Image(cur_voi.to_volume(), cur_voi.affine)
    header = img.get_header()
    header['qform_code'] = 1
    header['sform_code'] = 1
    img.update_header()
    return img


def console():
    main(sys.argv[1:])


if __name__ == "__main__":
    console()
