Azure
=====

This provider generates raw images for Microsoft Azure computing
platform.

Setup
-----

qemu-img >= 1.7.0 required to convert raw image to vhd fixed size disk.
This release is available in wheezy-backports.

*wget* must be installed on local computer.

Manifest must use the *raw* format, provider will automatically
transform the disk to a vhd disk format.

Do not create swap space on the OS disk:

The Windows Azure Linux Agent can automatically configure swap space
using the local resource disk that is attached to the VM after
provisioning on Azure. Modify the following parameters in
/etc/waagent.conf appropriately:

::

    ResourceDisk.Format=y
    ResourceDisk.Filesystem=ext4
    ResourceDisk.MountPoint=/mnt/resource
    ResourceDisk.EnableSwap=y
    ResourceDisk.SwapSizeMB=2048    ## NOTE: set this to whatever you need it to be.

You can specify a waagent.conf file to replace the default one in the
manifest in the azure/waagent section of the provider:

::

    "system" : { 
        "waagent" : {
           "conf": "path_to_my_conf_file",  # optional
           "version" : "2.0.4"              # mandatory
        }
    }, ...

Waagent versions are available at:
https://github.com/Azure/WALinuxAgent/releases
