#!/bin/sh
grep 'EXCLUDE_PATTERN' | grep --invert-match --fixed-strings 'INCLUDE_PATHS'
