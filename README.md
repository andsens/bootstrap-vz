bootstrap-vz
===========================================

bootstrap-vz is a fully automated bootstrapping tool for Debian.
It creates images for various virtualized platforms (at the moment: kvm, virtualbox, ec2).
The plugin architecture allows for heavy modification of standard behavior
(e.g. create a vagrant box, apply puppet manifests, run custom shell commands).

At no time is the resulting image booted, meaning there are no latent logfiles
or bash_history files.

The bootstrapper runs on a single json manifest file which contains all configurable
parameters. This allows you to recreate the image whenever you like so you can create
an updated version of an existing image or create the same image in multiple EC2 regions.

Dependencies
------------
You will need to run debian wheezy with **python 2.7** and **debootstrap** installed.
Other depencies include:
* qemu-utils
* parted
* grub2
* euca2ools
* xfsprogs (If you want to use XFS as a filesystem)
Also the following python libraries are required:
* **boto**
* **jsonschema** ([version 2.0.0](https://pypi.python.org/pypi/jsonschema), only available through pip)
* **termcolor**
* **fysom**

Bootstrapping instance store AMIs requires **euca2ools** to be installed.
