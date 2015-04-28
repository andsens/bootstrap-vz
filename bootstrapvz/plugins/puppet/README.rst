Puppet
------

Installs `puppet <http://puppetlabs.com/>`__ and optionally applies a
manifest inside the chroot. You can also have it copy your puppet
configuration into the image so it is readily available once the image
is booted.

Keep in mind that when applying a manifest, the system is in a chrooted
environment. This can prevent daemons from running properly (e.g.
listening to ports), they will also need to be shut down gracefully
(which bootstrap-vz cannot do) before unmounting the volume. It is
advisable to avoid starting any daemons inside the chroot at all.

Settings
~~~~~~~~

-  ``manifest``: Path to the puppet manifest that should be applied.
   ``optional``
-  ``assets``: Path to puppet assets. The contents will be copied into
   ``/etc/puppet`` on the image. Any existing files will be overwritten.
   ``optional``
-  ``enable_agent``: Whether the puppet agent daemon should be enabled.
   ``optional``
