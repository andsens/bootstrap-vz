Pip3 install
------------

Install packages from the Python Package Index via pip for python3

Installs ``build-essential`` and ``python3-dev`` debian packages, so
Python extension modules can be built.

Settings
~~~~~~~~

-  ``packages``: Python packages to install, a list of strings. The list
   can contain anything that ``pip install`` would accept as an
   argument, for example ``awscli==1.3.13``.
