#!/bin/sh
# First we filter out all paths not relating to the stuff we want to filter
# After that we take out the paths  that we *do* want to keep
grep 'EXCLUDE_PATTERN' | grep --invert-match --fixed-strings 'INCLUDE_PATHS'
