KVM provider
===========

This provider generates raw images for KVM.
It also supports an optional virtio integration.


Virtio
======

Add to bootstrapper the list of virtio modules to load, example:

    "virtio" : [ "virtio_pci", "virtio_blk" ]

