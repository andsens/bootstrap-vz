Manifest
========
The manifest file is the primary way to interact with bootstrap-vz.
Every configuration and customization of a Debian installation is specified in this file.

The manifest format is YAML or JSON. It is near impossible to run the
bootstrapper with an invalid configuration, since every part of the
framework supplies a `json-schema <http://json-schema.org/>`__ that
specifies exactly which configuration settings are valid in different
situations.

Manifest variables
------------------

Many of the settings in the example manifests use strings like
``debian-{system.release}-{system.architecture}-{{"{%y"}}}{{"{%m"}}}{{"{%d"}}}``.
These strings make use of manifest variables, which can cross reference
other settings in the manifest or specific values supplied by the
bootstrapper (e.g. all python date formatting variables are available).

Any reference uses dots to specify a path to the desired manifest
setting. Not all settings support this though, to see whether embedding
a manifest variable in a setting is possible, look for the
``manifest vars`` label.

Sections
--------

The manifest is split into 7 sections.

Provider
~~~~~~~~

The provider section contains all provider specific settings and the
name of the provider itself.

-  ``name``: target virtualization platform of the installation
   ``required``

Consult the `providers <../bootstrapvz/providers>`__ section of the documentation
for a list of valid values.

Bootstrapper
~~~~~~~~~~~~

This section concerns the bootstrapper itself and its behavior. There
are 4 possible settings:

-  ``workspace``: Path to where the bootstrapper should place images
   and intermediate files. Any volumes will be mounted under that path.
   ``required``
-  ``tarball``: debootstrap has the option to download all the
   software and pack it up in a tarball. When starting the actual
   bootstrapping process, debootstrap can then be pointed at that
   tarball and use it instead of downloading anything from the internet.
   If you plan on running the bootstrapper multiple times, this option
   can save you a lot of bandwidth and time. This option just specifies
   whether it should create a new tarball or not. It will search for and
   use an available tarball if it already exists, regardless of this
   setting.
   ``optional``
   Valid values: ``true, false``
   Default: ``false``
-  ``mirror``: The mirror debootstrap should download software from.
   It is advisable to specify a mirror close to your location (or the
   location of the host you are bootstrapping on), to decrease latency
   and improve bandwidth. If not specified, `the configured aptitude
   mirror URL <#packages>`__ is used.
   ``optional``
-  ``include_packages``: Extra packages to be installed during
   bootstrap. Accepts a list of package names.
   ``optional``
-  ``exclude_packages``: Packages to exclude during bootstrap phase.
   Accepts a list of package names.
   ``optional``
-  ``guest_additions``: This setting is only relevant for the
   `virtualbox provider <../bootstrapvz/providers/virtualbox>`__.
   It specifies the path to the VirtualBox Guest Additions ISO, which, when specified,
   will be mounted and used to install the VirtualBox Guest Additions.
   ``optional``

Image
~~~~~

The image section configures anything pertaining directly to the image
that will be created.

-  ``name``: The name of the resulting image.
   When bootstrapping cloud images, this would be the name visible in
   the interface when booting up new instances.
   When bootstrapping for VirtualBox or kvm, it's the filename of the
   image.
   ``required``
   ``manifest vars``
-  ``description``: Description of the image. Where this setting is
   used depends highly on which provider is set. At the moment it is
   only used for AWS images.
   ``required for ec2 provider``
   ``manifest vars``
-  ``bucket``: When bootstrapping an S3 backed image for AWS, this
   will be the bucket where the image is uploaded to.
   ``required for S3 backing``
-  ``region``: Region in which the AMI should be registered.
   ``required for S3 backing``

System
~~~~~~

This section defines anything that pertains directly to the bootstrapped
system and does not fit under any other section.

-  ``architecture``: The architecture of the system.
   Valid values: ``i386, amd64``
   ``required``
-  ``bootloader``: The bootloader for the system. Depending on the
   bootmethod of the virtualization platform, the options may be
   restricted.
   Valid values: ``grub, extlinux, pv-grub``
   ``required``
-  ``charmap``: The default charmap of the system.
   Valid values: Any valid charmap like ``UTF-8``, ``ISO-8859-`` or
   ``GBK``.
   ``required``
-  ``hostname``: hostname to preconfigure the system with.
   ``optional``
-  ``locale``: The default locale of the system.
   Valid values: Any locale mentioned in ``/etc/locale.gen``
   ``required``
-  ``release``: Defines which debian release should be bootstrapped.
   Valid values: ``squeeze``, ``wheezy``, ``jessie``, ``sid``,
   ``oldstable``, ``stable``, ``testing``, ``unstable``
   ``required``
-  ``timezone``: Timezone of the system.
   Valid values: Any filename from ``/usr/share/zoneinfo``
   ``required``

Packages
~~~~~~~~

The packages section allows you to install custom packages from a
variety of sources.

-  ``install``: A list of strings that specify which packages should
   be installed. Valid values: package names optionally followed by a
   ``/target`` or paths to local ``.deb`` files.
-  ``install_standard``: Defines if the packages of the
   ``"Standard System Utilities"`` option of the Debian installer,
   provided by `tasksel <https://wiki.debian.org/tasksel>`__, should be
   installed or not. The problem is that with just ``debootstrap``, the
   system ends up with very basic commands. This is not a problem for a
   machine that will not be used interactively, but otherwise it is nice
   to have at hand tools like ``bash-completion``, ``less``, ``locate``,
   etc.
   ``optional``
   Valid values: ``true``, ``false``
   Default: ``false``
-  ``mirror``: The default aptitude mirror.
   ``optional``
   Default: ``http://http.debian.net/debian``
-  ``sources``: A map of additional sources that should be added to
   the aptitude sources list. The key becomes the filename in
   ``/etc/apt/sources.list.d/`` (with ``.list`` appended to it), while
   the value is an array with each entry being a line.
   ``optional``
-  ``components``: A list of components that should be added to the
   default apt sources. For example ``contrib`` or ``non-free``
   ``optional``
   Default: ``['main']``
-  ``trusted-keys``: List of paths to ``.gpg`` keyrings that should
   be added to the aptitude keyring of trusted signatures for
   repositories.
   ``optional``
-  ``preferences``: Allows you to pin packages through `apt
   preferences <https://wiki.debian.org/AptPreferences>`__. The setting
   is an object where the key is the preference filename in
   ``/etc/apt/preferences.d/``. The key ``main`` is special and refers
   to the file ``/etc/apt/preferences``, which will be overwritten if
   specified.
   ``optional``
   The values are objects with three keys:
-  ``package``: The package to pin (wildcards allowed)
-  ``pin``: The release to pin the package to.
-  ``pin-priority``: The priority of this pin.

Volume
~~~~~~

bootstrap-vz allows a wide range of options for configuring the disk
layout of the system. It can create unpartitioned as well as partitioned
volumes using either the gpt or msdos scheme. At most, there are only
three partitions with predefined roles configurable though. They are
boot, root and swap.

-  ``backing``: Specifies the volume backing. This setting is very
   provider specific.
   Valid values: ``ebs``, ``s3``, ``vmdk``, ``vdi``, ``raw``
   ``required``
-  ``partitions``: A map of the partitions that should be created on
   the volume.
-  ``type``: The partitioning scheme to use. When using ``none``,
   only root can be specified as a partition.
   Valid values: ``none``, ``gpt``, ``msdos``
   ``required``
-  ``root``: Configuration of the root partition. ``required``

   -  ``size``: The size of the partition. Valid values: Any
      datasize specification up to TB (e.g. 5KiB, 1MB, 6TB).
      ``required``
   -  ``filesystem``: The filesystem of the partition. When choosing
      ``xfs``, the ``xfsprogs`` package will need to be installed.
      Valid values: ``ext2``, ``ext3``, ``ext4``, ``xfs``
      ``required``
   -  ``format_command``: Command to format the partition with. This
      optional setting overrides the command bootstrap-vz would normally
      use to format the partition. The command is specified as a string
      array where each option/argument is an item in that array (much
      like the `commands <../bootstrapvz/plugins/commands>`__ plugin).
      ``optional`` The following variables are available:
   -  ``{fs}``: The filesystem of the partition.
   -  ``{device_path}``: The device path of the partition.
   -  ``{size}``: The size of the partition.

   The default command used by boostrap-vz is
   ``['mkfs.{fs}', '{device_path}']``.

   -  ``boot``: Configuration of the boot partition. The three
      settings equal those of the root partition.
      ``optional``
   -  ``swap``: Configuration of the swap partition. Since the swap
      partition has its own filesystem you can only specify the size for
      this partition.
      ``optional``

Plugins
~~~~~~~

The plugins section is a map of plugin names to whatever configuration a
plugin requires. Go to the `plugin section <../bootstrapvz/plugins>`__
of the documentation, to see the configuration for a specific plugin.
