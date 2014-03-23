# Image script plugin

This plugin gives the possibility to the user to execute commands.

Plugin is defined in the manifest file, plugin section with:

    "image_commands": {
        "commands": [ [ "touch", "/var/www/index.html" ]],
    }

The *commands* element is an array of commands. Each command is an array describing the executable and its arguments.

Command is executed in current context. It is possible to use variables to access the image or execute chroot commands in the image.

Available variables are:
  {root} : image mount point (to copy files for example or chroot commands)

Example:

    [[ "touch", "{root}/var/www/hello" ],
    [ "/usr/sbin/chroot", "{root}", "touch", "/var/www/hello"]]

