#!/bin/bash
# This file was created by bootstrap-vz.
# See https://github.com/andsens/bootstrap-vz/blob/master/LICENSE for
# legal notices and disclaimers.

# Expands a partition and filesystem using growpart and an appropriate
# filesystem tool for live filesystem expansion. Takes three arguments:
# DEVICE, such as "/dev/sda"
# PARTITION, such as "1"
# FILESYSTEM, such as "ext4"

DEVICE="${1}"
PARTITION="${2}"
FILESYSTEM="${3}"

if [[ -z "${DEVICE}" || -z "${PARTITION}" || -z "${FILESYSTEM}" ]]; then
  echo "Requires: $0 DEVICE PARTITION FILESYSTEM"
  exit 1
fi

# Grow partition using growpart
if [[ -x /usr/bin/growpart ]]; then
  echo "Growing partition ${DEVICE}${PARTITION}"
  /usr/bin/growpart "${DEVICE}" "${PARTITION}"
else
  echo "/usr/bin/growpart was not found"
  exit 1
fi

echo "Resizing ${FILESYSTEM} filesystem on ${DEVICE}${PARTITION}"
case "${FILESYSTEM}" in
  xfs)  xfs_growfs / ;;
  ext2) resize2fs "${DEVICE}${PARTITION}" ;;
  ext3) resize2fs "${DEVICE}${PARTITION}" ;;
  ext4) resize2fs "${DEVICE}${PARTITION}" ;;
  *) echo "Unsupported filesystem,  unable to expand size." ;;
esac
