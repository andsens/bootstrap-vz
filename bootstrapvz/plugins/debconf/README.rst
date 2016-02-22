debconf
-------

``debconf(7)`` is the configuration system for Debian packages.
It enables you to preconfigure packages before their installation.

This plugin lets you specify debconf answers directly in the manifest.
You should only specify answers for packages that will be installed; the plugin
does not check that this is the case.

Settings
~~~~~~~~

The ``debconf`` plugin directly takes an inline string:::

  plugins:
    debconf: >-
      d-i pkgsel/install-language-support boolean false
      popularity-contest popularity-contest/participate boolean false


Consult ``debconf-set-selections(1)`` for a description of the data format.


