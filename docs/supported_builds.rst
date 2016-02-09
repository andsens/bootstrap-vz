Supported builds
================

The following is a list of supported manifest combinations.

Bootloaders and partitions
--------------------------

Note that grub cannot boot from unpartitioned volumes.

Azure
~~~~~

TODO


EC2
~~~

EBS
___

========================== ================= ================= =================
 Bootloader / Partitioning        none              msdos            gpt
========================== ================= ================= =================
 pvgrub (paravirtualized)      supported         supported         supported
 extlinux (hvm)                supported         supported         supported
 grub (hvm)                 *not supported*      supported         supported
========================== ================= ================= =================

S3
__

========================== ================= ================= =================
 Bootloader / Partitioning        none              msdos            gpt
========================== ================= ================= =================
 pvgrub (paravirtualized)      supported     *not implemented* *not implemented*
 extlinux (hvm)            *not implemented* *not implemented* *not implemented*
 grub (hvm)                 *not supported*  *not implemented* *not implemented*
========================== ================= ================= =================


GCE
~~~

TODO


KVM
~~~

TODO


Oracle
~~~~~~

TODO


VirtualBox
~~~~~~~~~~

========================== ================= ================= =================
 Bootloader / Partitioning        none              msdos            gpt
========================== ================= ================= =================
 extlinux                      supported         supported         supported
 grub                       *not supported*      supported         supported
========================== ================= ================= =================


Known working builds
--------------------

The following is a list of supported releases, providers and architectures
combination. We know that they are working because there's someone working
on them.

======= ======== ============ ===========================================================
Release Provider Architecture Person
======= ======== ============ ===========================================================
Jessie  EC2      ``amd64``    `James Bromberger <https://github.com/JamesBromberger>`__
Jessie  GCE      ``amd64``    `Zach Marano <https://github.com/zmarano>`__ (and GCE Team)
Jessie  KVM      ``arm64``    `Clark Laughlin <https://github.com/clarktlaugh>`__
Jessie  Oracle   ``amd64``    `Tiago Ilieve <https://github.com/myhro>`__
======= ======== ============ ===========================================================
