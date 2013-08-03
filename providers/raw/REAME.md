# RAW provider

This provider creates a raw image file. It can be combined with  opennebula plugin to add OpenNebula contextualization.

By default, it creates a network interface configured with DHCP.

# Configuration

## provider

*raw* : use this provider

##virtualization

* ide: basic disk emulation (/dev/sda)
* virtio: Virtio emulation (for KVM), provides better disk performances (/dev/vda)
