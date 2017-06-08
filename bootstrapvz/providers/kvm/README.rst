KVM
===

The `KVM <http://www.linux-kvm.org/page/Main_Page>`__ provider creates
virtual images for Linux Kernel-based Virtual Machines. It supports the
installation of `virtio kernel
modules <http://www.linux-kvm.org/page/Virtio>`__ (paravirtualized
drivers for IO operations).
It also supports creating an image with LVM as a disk backend.

Manifest settings
-----------------

Provider
~~~~~~~~

-  ``virtio``: Specifies which virtio kernel modules to install.
   ``optional``
-  ``logicalvolume``: Specifies the logical volume where the disk image will be built.
   ``volumegroup``: Specifies the volume group where the logical volume will be stored.
   These options should only be used if ``lvm`` was given as a disk backend.

Example:

.. code-block:: yaml

    ---
    provider:
      name: kvm
      virtio:
        - virtio_blk
        - virtio_net
    volume:
      backing: lvm
      logicalvolume: lvtest
      volumegroup: vgtest
