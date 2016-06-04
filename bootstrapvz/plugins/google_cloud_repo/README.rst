Google Cloud Repo
-----------------

This plugin adds support to use Google Cloud apt repositories for Debian. It adds the public repo key and optionally will add an apt source list file and install a package containing the key in order to maintain the key over time.

Settings
--------

-  ``cleanup_bootstrap_key``: Deletes the bootstrap key by removing /etc/apt/trusted.gpg in favor of the package maintained version. This is only to avoid having multiple keys around in the apt-key list. This should only be used with enable_keyring_repo.
-  ``enable_keyring_repo``: Add a repository and package to maintain the repo public key over time.
