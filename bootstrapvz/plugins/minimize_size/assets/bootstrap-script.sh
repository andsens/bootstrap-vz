#!/bin/sh

# This script does not override anything defined in /usr/share/debootstrap/scripts
# Instead we use it to redefine extract_dpkg_deb_data(), so that we may exclude
# certain files during bootstrapping.

extract_dpkg_deb_data () {
  local pkg="$1"
  local excludes_file="DEBOOTSTRAP_EXCLUDES_PATH"
  # List all files in $pkg and run them through the filter (avoid exit status >0 if no matches are found)
  dpkg-deb --fsys-tarfile "$pkg" | tar -t | BOOTSTRAP_FILES_FILTER_PATH > "$excludes_file" || true
  dpkg-deb --fsys-tarfile "$pkg" | tar --exclude-from "$excludes_file" -xf -
  rm "$excludes_file"
}

# Direct copypasta from the debootstrap script where it determines
# which script to run. We do exactly the same but leave out the
# if [ "$4" != "" ] part so that we can source the script that
# should've been sourced in this scripts place.

SCRIPT="$DEBOOTSTRAP_DIR/scripts/$SUITE"
if [ -n "$VARIANT" ] && [ -e "${SCRIPT}.${VARIANT}" ]; then
  SCRIPT="${SCRIPT}.${VARIANT}"
fi

. $SCRIPT
