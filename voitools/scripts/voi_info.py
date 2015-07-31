#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of the voitools package
# Copyright 2015 Board of Regents of the University of Wisconsin System
# Licensed under the MIT license; see LICENSE at the root of the package.

# Authored by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
# Imaging and Behavior.

"""Print information about a spamalize .voi file.

Usage:
  voi_info [options] <datafile>
  voi_info -h | --help

Options:
  -h --help                 Show this screen
  --version                 Show version
  -v --verbose              Display debugging information
"""

import sys
import voitools
from voitools import voi
import logging
from voitools.vendor import docopt


def main(argv):
    arguments = docopt.docopt(
        __doc__,
        argv,
        version="voitools {0}".format(voitools.__version__)
    )
    if arguments["--verbose"]:
        voi.logger.setLevel(logging.DEBUG)
    print_voi_info(arguments)


def print_voi_info(arguments):
    voi_data = voi.read_file(arguments['<datafile>'])
    print("VOI Group Header")
    for k, v in voi_data.header.iteritems():
        print("{0}: {1}".format(k, v))
    for i, cur_voi in enumerate(voi_data.vois):
        print("VOI {0} Header".format(i + 1))
        for k, v in cur_voi.header.iteritems():
            print("  {0}: {1}".format(k, v))


def console():
    main(sys.argv[1:])


if __name__ == "__main__":
    console()
