this provider creates images for KVM.

It is possible to add opennebula plugin for OpenNebula images.

Disk virtuzalition is specified by the virtualization field in the manifest.
Allowed values are:

* ide: basic disk emulation on /dev/sda1
* virtio: enhanced performance on /dev/vda1. It adds virtio modules in the kernel and needs configuration update in VM template: <target dev='vda' bus='virtio'/>
