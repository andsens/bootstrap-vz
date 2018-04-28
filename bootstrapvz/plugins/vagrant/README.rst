Vagrant
-------

Vagrant is a tool to quickly create virtualized environments. It uses
"boxes" to make downloading and sharing those environments easier. A box
is a tarball containing a virtual volumes accompanied by an `OVF
specification <http://en.wikipedia.org/wiki/Open_Virtualization_Format>`__
of the virtual machine.

This plugin creates a vagrant box that is ready to be shared or
deployed. At the moment it is only compatible with the VirtualBox
and Libvirt providers.

Settings
~~~~~~~~

-  ``provider``: Specifies the provider of a resulting vagrant box.
   ``optional`` Valid values: ``virtualbox, libvirt`` Default: ``libvirt``