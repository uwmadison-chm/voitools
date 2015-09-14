# -*- coding: utf-8 -*-
"""
Part of the voitools package
Copyright 2015 Board of Regents of the University of Wisconsin System
Licensed under the MIT license; see LICENSE at the root of the package.

Authored by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
Imaging and Behavior.
"""

from __future__ import (
    print_function,
    unicode_literals,
    division,
    absolute_import)

from collections import namedtuple
from voitools.vendor.ordereddict import OrderedDict
import numpy as np
import os

import logging
logger = logging.getLogger("voi")
logger.setLevel(logging.ERROR)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(ch)


Triple = namedtuple('Triple', ['x', 'y', 'z'])


def read_file(filename_or_io):
    if hasattr(filename_or_io, 'readline'):
        return _read_io(filename_or_io)
    else:
        with open(filename_or_io, 'r') as f:
            return _read_io(f)


def _read_io(io):
    voi_group = VOIGroup.from_io(io)
    for i in range(voi_group.voi_count):
        VOI.from_io(voi_group, io)
    return voi_group


class VOIGroup(object):
    def __init__(self, header, vois=None, affine=None):
        super(VOIGroup, self).__init__()
        self.header = header
        self.vois = vois or []
        self.__affine = affine

    BEGIN_HEADER = "******** VOIGroup File *********"
    END_HEADER = "-----------------------------------"

    @classmethod
    def from_io(kls, io):
        """
        readable is assumed to be seek()ed to the start of the data -- in this
        case, that will generally be the start of the file.
        """
        header = OrderedDict()
        header_start_line = io.readline().strip()
        if not header_start_line == kls.BEGIN_HEADER:
            raise VOIFileError(
                "file does not start with {0}".format(kls.BEGIN_HEADER))
        while True:
            line = io.readline().strip()
            logger.debug("Main header read {0}".format(line))
            if line == kls.END_HEADER:
                logger.debug("Main header end")
                break
            parts = [p.strip() for p in line.split("=", 1)]
            if len(parts) == 2:
                k, v = parts
                logger.debug("Setting {0} to {1}".format(k, v))
                header[parts[0]] = parts[1]
        return kls(header)

    @property
    def data_type_string(self):
        return {
            "BIG_ENDIAN": ">i4",
            "LITTLE_ENDIAN": "<i4"
        }[self.header["Byte Order"]]

    @property
    def voi_count(self):
        return int(self.header['Number of VOIs'])

    @property
    def voxel_dimensions(self):
        return Triple(
            float(self.header['X pixdim']),
            float(self.header['Y pixdim']),
            float(self.header['Z pixdim']),
        )

    @property
    def shape(self):
        return Triple(
            x=int(self.header['X dim']),
            y=int(self.header['Y dim']),
            z=int(self.header['Z dim']),
        )

    @property
    def affine(self):
        if self.__affine is not None:
            return self.__affine
        return self.__centered_affine

    def set_affine(self, aff):
        self.__affine = aff

    @property
    def using_default_affine(self):
        return self.__affine is None

    @property
    def __center_coords(self):
        shape = np.array(self.shape)
        voxdims = np.array(self.voxel_dimensions)
        center = (-0.5 * shape * voxdims) + (0.5 * voxdims)
        return center

    @property
    def __centered_affine(self):
        # Our -1, -1, 1 contortions bring us into RAI coordinates.
        # I don't know if this is always needed
        voxel_dims = np.array(list(self.voxel_dimensions) + [1.0])
        affine = np.diag(voxel_dims * np.array([-1, -1, 1, 1]))
        affine[:, 3][0:3] = self.__center_coords * np.array([-1, -1, 1])
        return affine


class VOI(object):
    def __init__(self, voi_group, header, voxel_indexes):
        super(VOI, self).__init__()
        self.voi_group = voi_group
        self.header = header
        self.voxel_indexes = voxel_indexes
        self.voi_group.vois.append(self)

    BEGIN_HEADER = "VOI"
    BEGIN_DATA = "Start voxel data"
    END_VOI = "End of VOI"

    @classmethod
    def from_io(kls, voi_group, io):
        """
        Read the header and voxel indexes. Assumes io is seek()ed to the start
        of the VOI header (eg, the next bytes we read should be "VOI").
        Transforms text triples into voxel indexes.
        When done, we will be seek()ed to the start of the next VOI, or eof.
        """
        header = kls._read_header(io)
        voi = kls(voi_group, header, None)
        voi._read_data(io)
        voi._seek_to_next_voi(io)
        return voi

    @classmethod
    def _read_header(kls, io):
        header = OrderedDict()
        header_start_line = io.readline().strip()
        if not header_start_line == kls.BEGIN_HEADER:
            raise VOIFileError(
                "voi does not start with {0}".format(kls.BEGIN_HEADER))
        while True:
            line = io.readline().strip()
            logger.debug("VOI header read {0}".format(line))
            parts = [p.strip() for p in line.split("=", 1)]
            if len(parts) == 2:
                k, v = parts
                header[k] = v
                if k == kls.BEGIN_DATA:
                    logger.debug("VOI header end, data starts")
                    break
        return header

    @property
    def voxel_count(self):
        return int(self.header['Number of voxels'])

    @property
    def shape(self):
        return Triple(
            x=int(self.header['x_dim']),
            y=int(self.header['y_dim']),
            z=int(self.header['z_dim']),
        )

    @property
    def voxel_dimensions(self):
        return Triple(
            x=float(self.header['x_pixdim']),
            y=float(self.header['y_pixdim']),
            z=float(self.header['z_pixdim']),
        )

    @property
    def name(self):
        return self.header['VOI name']

    @property
    def voi_name(self):
        return self.name

    @property
    def base_name(self):
        f = os.path.basename(self.voi_group.header['Image-base file name'])
        noext = os.path.splitext(f)[0]
        return noext

    @property
    def cur_name(self):
        f = os.path.basename(self.voi_group.header['Current file name'])
        noext = os.path.splitext(f)[0]
        return noext

    @property
    def voi_number(self):
        return self.header['VOI number']

    @property
    def affine(self):
        return self.voi_group.affine

    def to_volume(self, dtype=np.int16):
        vol = np.zeros(self.shape, dtype=dtype, order='F')
        raveled = vol.ravel('A')
        raveled[self.voxel_indexes] = 1
        return vol

    def _read_data(self, io):
        self.__read_data_fx(io)

    @property
    def __read_data_fx(self):
        """
        The "Start voxel data" header tells us what format the voxels are
        going to be in; find the corresponding function and call it.
        """
        return {
            "Text coordinate triple": self.__read_data_text_triples,
            "Text coordinate index": self.__read_data_text_indexes,
            "LONG coordinate index": self.__read_data_long_indexes,
        }[self.header["Start voxel data"]]

    def __read_data_long_indexes(self, io):
        """
        This data is a bunch of 32-bit ints strung together.
        """
        logger.debug("Reading long index data")
        self.voxel_indexes = np.fromfile(
            io,
            self.voi_group.data_type_string,
            self.voxel_count)

    def __read_data_text_indexes(self, io):
        """
        This is a set of text indexes, one per line
        """
        logger.debug("Reading text index data")
        self.voxel_indexes = np.zeros(self.voxel_count, dtype=np.int32)
        for i in range(self.voxel_count):
            idx = int(io.readline.strip())
            self.voxel_indexes[i] = idx

    def __triple_to_index(self, x, y, z):
        return ((z * self.shape.x * self.shape.y) + (y * self.shape.x) + x)

    def __read_data_text_triples(self, io):
        """
        This is a set of integer triples in the format
        x, y, z
        We'll convert these to voxel indexes and return a numpy array of
        those.
        """
        logger.debug("Reading text triple data")

        def triple_line_to_index(line):
            x, y, z = [int(num) for num in line.split(",")]
            return self.__triple_to_index(x, y, z)

        self.voxel_indexes = np.zeros(self.voxel_count, dtype=np.int32)
        for i in range(self.voxel_count):
            triple_text = io.readline().strip()
            idx = triple_line_to_index(triple_text)
            logger.debug("Triple {0} -> {1}".format(triple_text, idx))
            self.voxel_indexes[i] = idx

    def _seek_to_next_voi(self, io):
        """
        Assumes we're at the end of our voxel data, we'll read lines until we
        get to END_VOI, and then another couple to leave us at the start of
        the next VOI header.
        """
        while True:
            line = io.readline()
            parts = [p.strip() for p in line.split("=")]
            if len(parts) == 2 and parts[0] == self.END_VOI:
                break
        # There are two lines we can ignore here...
        io.readline()
        io.readline()

    def __repr__(self):
        return "VOI #{0}: {1}, {2} voxels".format(
            self.header["VOI number"],
            self.name,
            self.voxel_count)


class VOIFileError(ValueError):
    pass
