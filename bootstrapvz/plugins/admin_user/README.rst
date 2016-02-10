Admin user
----------

This plugin creates a user with passwordless sudo privileges. It also
disables the SSH root login. There are three ways to grant access to
the admin user:
-  Set a password for the user, or
-  Provide a ssh public key to allow remote ssh login, or
-  Use the EC2 public key (EC2 machines only)

If a password is provided, this plugin sets the admin password. This
also re-enables password login (off by default in Jessie).

If the optional argument pubkey is present (it should be a full path
to a ssh public key), it will ensure that the ssh public key is used
to set up password less remote login for the admin user.

Only one of these options (password, or pubkey) may be specified.

If neither the password not a ssh public key location are specified,
and if the EC2 init scripts are installed, the script for fetching the
SSH authorized keys will be adjust to match the username specified.

Settings
~~~~~~~~

-  ``username``: The username of the account to create. ``required``
-  ``password``: An optional password for the account to create. ``optional``
-  ``pubkey``:   The full path to an ssh public key to allow
   remote access into the admin account. ``optional``
