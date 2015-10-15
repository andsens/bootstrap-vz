Azure
=====

This provider generates raw images for Microsoft Azure computing
platform.

Setup
-----

``qemu-utils`` is needed to create the VHD image.

``wget`` must be installed on local computer, so the Windows Azure Linux Agent
can be downloaded.

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
