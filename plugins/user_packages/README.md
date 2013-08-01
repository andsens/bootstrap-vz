# User package plugin

This plugin gives the possibility to the user to install Debian packages in the virtual image.

Plugin is defined in the manifest file, plugin section with:

    "user_packages": {
        "enabled": true,
        "repo": [ "apache2" ],
        "local": [ "/tmp/mypackage.deb" ]
    }

The *repo* element refers to packages available in Debian repository (apt-get).

The *local* element will copy the specified .deb files and install them in the image with a dpkg command. Packages are installed in the order of their declaration.
