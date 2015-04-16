Supported builds
================

The following is a list of supported manifest combinations.

Note that grub cannot boot from unpartitioned volumes.

Additionally grub installation is not supported on *squeeze*.
This is not a technical limitation, but simply stems from a
lack of motivation to implement support for it.

Azure
-----

TODO


EC2
---

EBS (wheezy & jessie)
~~~~~~~~~~~~~~~~~~~~~

========================== ================= ================= =================
 Bootloader / Partitioning        none              msdos            gpt
========================== ================= ================= =================
 pvgrub (paravirtualized)      supported         supported         supported
 extlinux (hvm)                supported         supported         supported
 grub (hvm)                 *not supported*      supported         supported
========================== ================= ================= =================

EBS (squeeze)
~~~~~~~~~~~~~

========================== ================= ================= =================
 Bootloader / Partitioning        none              msdos            gpt
========================== ================= ================= =================
 pvgrub (paravirtualized)      supported         supported         supported
 extlinux (hvm)                supported         supported         supported
 grub (hvm)                 *not supported*  *not implemented* *not implemented*
========================== ================= ================= =================

S3 (all releases)
~~~~~~~~~~~~~~~~~

========================== ================= ================= =================
 Bootloader / Partitioning        none              msdos            gpt
========================== ================= ================= =================
 pvgrub (paravirtualized)      supported     *not implemented* *not implemented*
 extlinux (hvm)            *not implemented* *not implemented* *not implemented*
 grub (hvm)                 *not supported*  *not implemented* *not implemented*
========================== ================= ================= =================

GCE
---

TODO

KVM
---

TODO


VirtualBox
----------

========================== ================= ================= =================
 Bootloader / Partitioning        none              msdos            gpt
========================== ================= ================= =================
 extlinux                      supported         supported         supported
 grub                       *not supported*      supported         supported
========================== ================= ================= =================
