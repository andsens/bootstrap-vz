Docker daemon
-------------

Install `docker <http://www.docker.io/>`__ daemon in the image. Uses
init scripts for the official repository.

This plugin can only be used if the distribution being bootstrapped is
at least ``wheezy``, as Docker needs a kernel version ``3.8`` or higher,
which is available at the ``wheezy-backports`` repository. There's also
an architecture requirement, as it runs only on ``amd64``.

Settings
~~~~~~~~

-  ``version``: Selects the docker version to install. To select the
   latest version simply omit this setting.
   Default: ``latest``
   ``optional``
