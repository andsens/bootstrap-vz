Admin user
----------

This plugin creates a user with passwordless sudo privileges. It also
disables the SSH root login. If the EC2 init scripts are installed, the
script for fetching the SSH authorized keys will be adjust to match the
username specified.

Settings
~~~~~~~~

-  ``username``: The username of the account to create. ``required``
