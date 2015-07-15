# -*- coding: utf-8 -*-
"""
Part of the voitools package
Copyright 2015 Board of Regents of the University of Wisconsin System
Licensed under the MIT license; see LICENSE at the root of the package.

Authored by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
Imaging and Behavior.

This contains tests for the voi_info script
"""

from __future__ import (
    print_function,
    unicode_literals,
    division,
    absolute_import)


from voitools.scripts import voi_info

import pytest


def test_voitools_runs(capsys):
    with pytest.raises(SystemExit):
        voi_info.main(['--help'])
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert len(err) == 0


def test_voitools_reads_long_file(long_data_filename, capsys):
    voi_info.main([long_data_filename])
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert len(err) == 0


def test_voitools_reads_triple_file(triple_data_filename, capsys):
    voi_info.main([triple_data_filename])
    out, err = capsys.readouterr()
    assert len(out) > 0
    assert len(err) == 0
