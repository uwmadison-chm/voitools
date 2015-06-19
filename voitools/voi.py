# -*- coding: utf-8 -*-
"""
Part of the voitools package
Copyright 2015 Board of Regents of the University of Wisconsin System
Licensed under the MIT license; see LICENSE at the root fo the package.

Authored by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
Imaging and Behavior.
"""

from __future__ import (
    print_function,
    unicode_literals,
    division,
    absolute_import)

from collections import namedtuple
import numpy as np

import logging
logger = logging.getLogger("voi")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(ch)


Triple = namedtuple('Triple', ['x', 'y', 'z'])


class VOIGroup(object):
    def __init__(self, header, vois=[]):
        super(VOIGroup, self).__init__()
        self.header = header
        self.vois = vois

    BEGIN_HEADER = "******** VOIGroup File *********"
    END_HEADER = "-----------------------------------"

    @classmethod
    def from_io(kls, io):
        """
        readable is assumed to be seek()ed to the start of the data -- in this
        case, that will generally be the start of the file.
        """
        header = {}
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


class VOI(object):
    def __init__(self, voigroup, header, voxel_indexes):
        super(VOI, self).__init__()
        self.voigroup = voigroup
        self.header = header
        self.voxel_indexes = voxel_indexes

    BEGIN_HEADER = "VOI"
    BEGIN_DATA = "Start voxel data"
    END_VOI = "End of VOI"

    @classmethod
    def from_io(kls, voigroup, io):
        """
        Read the header and voxel indexes. Assumes io is seek()ed to the start
        of the VOI header (eg, the next bytes we read should be "VOI").
        Transforms text triples into voxel indexes.
        When done, we will be seek()ed to the start of the next VOI, or eof.
        """
        header = kls.read_header(io)
        voi = kls(voigroup, header, None)
        voi.read_data(io)
        return voi

    @classmethod
    def read_header(kls, io):
        header = {}
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

    def read_data(self, io):
        self.__read_data_fx(io)

    @property
    def __read_data_fx(self):
        return {
            "Text coordinate triple": self.__read_data_text_triples,
            "Text coordinate index": self.__read_data_text_indexes,
            "LONG coordinate index": self.__read_data_long_indexes,
        }[self.header["Start voxel data"]]

    def __read_data_long_indexes(self, io):
        logger.debug("Reading LONG data!")
        self.voxel_indexes = np.fromfile(
            io,
            self.voigroup.data_type_string,
            self.voxel_count)

    def __read_data_text_indexes(self, io):
        pass

    def __read_data_text_triples(self, io):
        pass


class VOIFileError(ValueError):
    pass
