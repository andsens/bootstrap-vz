Expand Root
-----------

This plugin adds support to expand the root partition and filesystem dynamically on boot. It adds a shell script to call growpart and the proper filesystem expansion tool for a given device, partition, and filesystem. The growpart script is part of the cloud-guest-utils package in stretch and jessie-backports. The version of this script in jessie is broken in several ways and so this plugin installs the version from jessie-backports which works correctly. This plugin should not be used in conjunction with common.tasks.initd.AddExpandRoot and common.tasks.initd.AdjustExpandRootScript. It is meant to replace the existing internal common version of expand-root.

Settings
~~~~~~~~

-  ``filesystem_type``: The type of filesystem to grow, one of ext2, ext3, ext4, of xfs.
-  ``root_device``: The root device we are growing, /dev/sda as an example.
-  ``root_partition``: The root partition ID we are growing, 1 (which becomes /dev/sda1). This is specified so you could grow a different partition on the root_device if you have a multi partition setup and because growpart takes the partition number as a separate argument.
