Azure
=====

This provider generates raw images for Microsoft Azure computing
platform.


Manifest settings
-----------------

Provider
~~~~~~~~

-  ``waagent``: Waagent specific settings.
   ``required``

    -  ``conf``: Path to ``waagent.conf`` that should override the default
       ``optional``
    -  ``version``: Version of waagent to install.
       Waagent versions are available at:
       https://github.com/Azure/WALinuxAgent/releases
       ``required``

Example:

.. code-block:: yaml

    ---
    provider:
      name: azure
      waagent:
        conf: /root/waagent.conf
        version: 2.0.4

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

