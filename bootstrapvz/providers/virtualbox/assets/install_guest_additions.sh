#!/bin/bash

function uname {
  if [[ $1 == '-r' ]]; then
    echo "KERNEL_VERSION"
    return 0
  elif [[ $1 == '-m' ]]; then
    echo "KERNEL_ARCH"
    return 0
  else
    $(which uname) $@
  fi
}
export -f uname

INSTALL_SCRIPT --nox11
