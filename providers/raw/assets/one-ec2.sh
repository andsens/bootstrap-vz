#!/bin/bash

if [ -n "$EC2_USER_DATA" ]; then
  # Check if EC2 user data is a script, if yes, execute
  if [[ $EC2_USER_DATA =~ ^#! ]]; then
    echo "EC2 data is an executable script, so execute it now"
    TMPFILE=$(mktemp /tmp/output.XXXXXXXXXX)
    chmod 755 $TMPFILE
    $TMPFILE
    cat $TMPFILE
  else
    print "Not an executable"
  fi
fi
