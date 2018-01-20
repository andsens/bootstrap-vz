#!/bin/sh
# This file was created by bootstrap-vz.
# See https://github.com/andsens/bootstrap-vz/blob/master/LICENSE for
# legal notices and disclaimers.

# First we filter out all paths not relating to the stuff we want to filter
# After that we take out the paths  that we *do* want to keep
grep 'EXCLUDE_PATTERN' | grep --invert-match --fixed-strings 'INCLUDE_PATHS'
