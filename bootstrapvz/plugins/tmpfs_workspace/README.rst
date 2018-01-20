tmpfs workspace
---------------

The ``tmpfs workspace`` plugin mounts a tmpfs filesystem for the
workspace temporary files. This is useful when the workspace directory
is placed on a slow medium (e.g. a hard disk drive), the build process
performs lots of local I/O (e.g. building a vagrant box), and there is
enough RAM to store data necessary for the build process. For example,
the ``stretch-vagrant.yml`` manifest file from the examples directory
takes 33 minutes to build on the plugin author's home server. Using
this plugin reduces this time to 3 minutes at the cost of 1.2GB of
additional RAM usage.

Settings
~~~~~~~~

This plugin has no settings. To enable it add ``"tmpfs_workspace":{}``
to the plugin section of the manifest.
