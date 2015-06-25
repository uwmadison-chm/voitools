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

import voitools
from voitools.vendor import docopt


def main():
    arguments = docopt.docopt(
        __doc__,
        version="voitools {0}".format(voitools.__version__)
    )
    print_voi_info(arguments)


def print_voi_info(arguments):
    pass


if __name__ == "__main__":
    main()
