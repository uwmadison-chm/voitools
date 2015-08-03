# voitools

Scripts of inspect volume-of-interest files created by [spamalize](http://brainimaging.waisman.wisc.edu/~oakes/spam/spam_frames.htm), and convert them into NIFTI images.

Requires [nibabel](http://nipy.sourceforge.net/nibabel/) and, hence, numpy. Should work with python 2.6 and 2.7; 3.0 is not tested yet.

## Installation

```python setup.py install```

After some testing, I'll put this up on pypi.

## Usage

### voi2nii

```
voi2nii [options] <datafile>

Convert a spamalize .voi file into a set of nifti files.

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
  --out-dir=<dir>       Directory to write the output files [default: .]
  -h --help             Show this screen
  --version             Show version
  -v --verbose          Display debugging information
```

### voi_info

```
voi_info [options] <datafile>

Print information about a spamalize .voi file.

Usage:
  voi_info [options] <datafile>
  voi_info -h | --help

Options:
  -h --help                 Show this screen
  --version                 Show version
  -v --verbose              Display debugging information
```

## Notes

Spamalize is written in IDL; its arrays are in fortran data order. Orientation and origin information are not included in .voi files; voi2nii writes in RAI orientation with the origin at the center of the volume.

## Credits

[Spamalize](http://brainimaging.waisman.wisc.edu/~oakes/spam/spam_frames.htm) was developed by the most skilled and fantastic Terry Oakes.

voi_tools ships with the excellent [docopt](http://docopt.org/) and ordereddict libraries.

docopt is copyright © 2013 Vladimir Keleshev, vladimir@keleshev.com

ordereddict is copyright © 2009 Raymond Hettinger


