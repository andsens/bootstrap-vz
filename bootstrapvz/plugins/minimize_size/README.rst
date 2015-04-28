minimize size
-------------

This plugin can be used to reduce the size of the resulting image. Often
virtual volumes are much smaller than their reported size until any data
is written to them. During the bootstrapping process temporary data like
the aptitude cache is written to the volume only to be removed again.

The minimize size plugin employs three different strategies to keep a
low volume footprint:

-  Mount folders from the host into key locations of the image volume to
   avoid any unneccesary disk writes.
-  Use `zerofree <http://intgat.tigress.co.uk/rmy/uml/index.html>`__ to
   deallocate unused sectors on the volume. On an unpartitioned volume
   this will be done for the entire volume, while it will only happen on
   the root partition for partitioned volumes.
-  Use
   `vmware-vdiskmanager <https://www.vmware.com/support/ws45/doc/disks_vdiskmanager_eg_ws.html>`__
   to shrink the real volume size (only applicable when using vmdk
   backing). The tool is part of the `VMWare
   Workstation <https://my.vmware.com/web/vmware/info/slug/desktop_end_user_computing/vmware_workstation/10_0>`__
   package.

Settings
~~~~~~~~

-  ``zerofree``: Specifies if it should mark unallocated blocks as
   zeroes, so the volume could be better shrunk after this.
   Valid values: true, false
   Default: false
   ``optional``
-  ``shrink``: Whether the volume should be shrunk. This setting works
   best in conjunction with the zerofree tool.
   Valid values: true, false
   Default: false
   ``optional``
