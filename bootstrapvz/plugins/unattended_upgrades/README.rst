Unattended upgrades
-------------------

Enables the `unattended update/upgrade
feature <https://packages.debian.org/wheezy/unattended-upgrades>`__ in
aptitude. Enable it to have your system automatically download and
install security updates automatically with a set interval.

Settings
~~~~~~~~

-  ``update_interval``: Days between running ``apt-get update``.
   ``required``
-  ``download_interval``: Days between running
   ``apt-get upgrade --download-only``
   ``required``
-  ``upgrade_interval``: Days between installing any security upgrades.
   ``required``
