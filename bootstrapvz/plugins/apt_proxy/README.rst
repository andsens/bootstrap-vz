APT Proxy
---------

This plugin creates a proxy configuration file for APT, so you could
enjoy the benefits of using cached packages instead of downloading them
from the mirror every time. You could just install ``apt-cacher-ng`` on
the host machine and then add ``"address": "127.0.0.1"`` and
``"port": 3142`` to the manifest file.

Settings
~~~~~~~~

-  ``address``: The IP or host of the proxy server.
    *``required``*
-  ``port``: The port (integer) of the proxy server.
    *``required``*
-  ``persistent``: Whether the proxy configuration file should remain on
   the machine or not.
   Valid values: true, false
   Default: ``false``
   *``optional``*
