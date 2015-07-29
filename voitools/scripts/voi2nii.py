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
                        [default: {base_name}-{voi_number}.nii]
  --voi-numbers=<nums>  The indexes (starting from 1) of the VOIs to convert.
                        Separate with commas. If not specified, converts all
                        VOIs.
  --out-dir=<dir>       Directory to write the output files [default: .]
  -h --help             Show this screen
  --version             Show version
  -v --verbose          Display debugging information
"""

import sys
import logging
import re
import os

import numpy as np
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
    voi_numbers = None
    if arguments['--voi-numbers']:
        parts = arguments['--voi-numbers'].split(",")
        voi_numbers = [int(num) - 1 for num in parts]
    voi_group = voitools.voi.read_file(arguments['<datafile>'])
    process_vois(
        voi_group,
        arguments['--pattern'],
        voi_numbers,
        arguments['--out-dir'])


def make_filename(pattern, voi):
    out_name = pattern
    for attr in PATTERN_SUBS:
        val = getattr(voi, "{0}".format(attr))
        val_safe = re.sub(WORD_CHAR_RE, "_", str(val))
        out_name = out_name.replace(
            "{{{0}}}".format(attr), str(val_safe))
    return out_name


def process_vois(voi_group, name_pattern, voi_numbers, out_dir):
    voi_numbers = voi_numbers or range(voi_group.voi_count)
    for num in voi_numbers:
        logger.debug("Converting VOI {0}".format(num + 1))
        voi = voi_group.vois[num]
        out_filename = os.path.join(out_dir, make_filename(name_pattern, voi))
        logger.info("Writing to {0}".format(out_filename))
        img = nib.Nifti1Image(voi.to_volume(), voi_group.affine)
        img.header['qform_code'] = 1
        img.header['sform_code'] = 1
        img.update_header()
        img.to_filename(out_filename)


if __name__ == "__main__":
    main(sys.argv[1:])
