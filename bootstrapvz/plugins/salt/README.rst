Salt
----

Install `salt <http://www.saltstack.com/>`__ minion in the image. Uses
`salt-bootstrap <https://github.com/saltstack/salt-bootstrap>`__ script
to install.

Settings
~~~~~~~~

-  ``install_source``: Source to install salt codebase from. ``stable``
   for current stable, ``daily`` for installing the daily build, and
   ``git`` to install from git repository.
   ``required``
-  ``version``: Only needed if you are installing from ``git``.
   \ ``develop`` to install current development head, or provide any tag
   name or commit hash from `salt
   repo <https://github.com/saltstack/salt>`__
   ``optional``
-  ``master``: Salt master FQDN or IP
   ``optional``
-  ``grains``: Set `salt
   grains <http://docs.saltstack.com/en/latest/topics/targeting/grains.html>`__
   for this minion. Accepts a map with grain name as key and the grain
   data as value.
   ``optional``
