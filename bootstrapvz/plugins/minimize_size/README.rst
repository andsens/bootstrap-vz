minimize size
-------------

This plugin can be used to reduce the size of the resulting image. Often
virtual volumes are much smaller than their reported size until any data
is written to them. During the bootstrapping process temporary data like
the aptitude cache is written to the volume only to be removed again.

The minimize size plugin employs various strategies to keep a low volume
footprint:

-  Mount folders from the host into key locations of the image volume to
   avoid any unnecessary disk writes.
-  Use `zerofree <http://intgat.tigress.co.uk/rmy/uml/index.html>`__ to
   deallocate unused sectors on the volume. On an unpartitioned volume
   this will be done for the entire volume, while it will only happen on
   the root partition for partitioned volumes.
-  Shrink the real volume size. Supported tools are:

   -  `vmware-vdiskmanager <https://www.vmware.com/support/ws45/doc/disks_vdiskmanager_eg_ws.html>`__
      (only applicable when using vmdk backing). The tool is part of the
      `VMWare Workstation <https://my.vmware.com/web/vmware/info/slug/desktop_end_user_computing/vmware_workstation/10_0>`__
      package.
   -  `qemu-img` (only applicaple when using vmdk, vdi, raw or qcow2 backing). This
      tool is part of the `QEMU emulator <https://www.qemu.org/>`__.

-  Tell apt to only download specific language files. See the
   `apt.conf manpage <http://manpages.debian.org/cgi-bin/man.cgi?query=apt.conf>`__
   for more details ("Languages" in the "Acquire group" section).
-  Configure debootstrap and dpkg to filter out specific paths when installing packages


Settings
~~~~~~~~

-  ``zerofree``: Specifies if it should mark unallocated blocks as
   zeroes, so the volume could be better shrunk after this.
   Valid values: true, false
   Default: false
   ``optional``
-  ``shrink``: Whether the volume should be shrunk. This setting works
   best in conjunction with the zerofree tool. Valid values:

   -  false: Do not shrink.
   -  ``vmware-vdiskmanager`` or true: Shrink using the `vmware-vdiskmanager`
      utility.
   -  ``qemu-img``: Shrink using the `qemu-img` utility.

   Default: false
   ``optional``
-  ``apt``: Apt specific configurations. ``optional``

   -  ``autoclean``: Configure apt to clean out the archive and cache
      after every run.
      Valid values: true, false
      Default: false
      ``optional``
   -  ``languages``: List of languages apt should download. Use ``[none]`` to
      not download any languages at all.
      ``optional``
   -  ``gzip_indexes``: Gzip apt package indexes.
      Valid values: true, false
      Default: false
      ``optional``
   -  ``autoremove_suggests``: Suggested packages are removed when running.
      ``apt-get purge --auto-remove``
      Valid values: true, false
      Default: false
      ``optional``
-  ``dpkg``: dpkg (and debootstrap) specific configurations.
   These settings not only affect the behavior of dpkg when
   installing packages after the image has been created, but also
   during the bootstrapping process. This includes the behavior of
   debootstrap.
   ``optional``

   -  ``locales``: List of locales that should be kept.
      When this option is used, all locales (and the manpages in those locales)
      are excluded from installation excepting the ones in this list.
      Specify an empty list to not install any locales at all.
      ``optional``
   -  ``exclude_docs``: Exclude additional package documentation located in
      ``/usr/share/doc``
      Valid values: true, false
      Default: false
      ``optional``
