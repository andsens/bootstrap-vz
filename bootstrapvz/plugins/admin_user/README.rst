Admin user
----------

This plugin creates a user with passwordless sudo privileges. It also
disables the SSH root login. There are three ways to grant access to
the admin user:
-  Use the EC2 public key (EC2 machines only)
-  Set a password for the user
-  Provide a SSH public key to allow remote SSH login

If the EC2 init scripts are installed, the script for fetching the
SSH authorized keys will be adjusted to match the username
specified in ``username``.

If a password is provided (the ``password`` setting),
this plugin sets the admin password, which also re-enables
SSH password login (off by default in Jessie or newer).

If the optional setting ``pubkey`` is present (it should be a full path
to a SSH public key), you will be able to log in to the admin user account
using the corresponding private key
(this disables the EC2 public key injection mechanism).

The ``password`` and ``pubkey`` settings can be used at the same time.

Settings
~~~~~~~~

-  ``username``: The username of the account to create. ``required``
-  ``password``: An optional password for the account to create. ``optional``
-  ``pubkey``:   The full path to an SSH public key to allow
   remote access into the admin account. ``optional``

Example:

.. code-block:: yaml

    ---
    plugins:
      admin_user:
        username: admin
        password: s3cr3t
        pubkey: /home/bootstrap-vz/.ssh/id_rsa
