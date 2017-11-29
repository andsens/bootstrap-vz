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

To insert a literal ``{foo}`` use double braces, that is ``{{foo}}``.
For example in a shell command where you may want to use the
expression ``${foo}``, use ``${{foo}}`` instead.

Sections
--------

The manifest is split into 7 sections.

Name
~~~~~

Single string property that specifies the name of the image.

-  ``name``: The name of the resulting image.
   When bootstrapping cloud images, this would be the name visible in
   the interface when booting up new instances.
   When bootstrapping for VirtualBox or kvm, it's the filename of the
   image.
   ``required``
   ``manifest vars``

Example:

.. code:: yaml

    ---
    name: debian-{system.release}-{system.architecture}-{%Y}-{%m}-{%d}-ebs

Provider
~~~~~~~~

The provider section contains all provider specific settings and the
name of the provider itself.

-  ``name``: target virtualization platform of the installation
   ``required``

Consult the `providers <../bootstrapvz/providers>`__ section of the documentation
for a list of valid values.


Example:

.. code:: yaml

    ---
    provider:
      name: ec2

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
-  ``variant``: Debian variant to install. The only supported value
   is ``minbase`` and should only be used in conjunction with the
   Docker provider. Not specifying this option will result in a normal
   Debian variant being bootstrapped.


Example:

.. code:: yaml

    ---
    bootstrapper:
      workspace: /target
      tarball: true
      mirror: http://deb.debian.org/debian/
      include_packages:
         - whois
         - psmisc
      exclude_packages:
         - isc-dhcp-client
         - isc-dhcp-common
      variant: minbase

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

Example:

.. code:: yaml

    ---
    system:
      release: jessie
      architecture: amd64
      bootloader: extlinux
      charmap: UTF-8
      hostname: jessie x86_64
      locale: en_US
      timezone: UTC

Packages
~~~~~~~~

The packages section allows you to install custom packages from a
variety of sources.

-  ``install``: A list of strings that specify which packages should
   be installed. Valid values: Package names optionally followed by a
   ``/target`` or paths to local ``.deb`` files.
   Note that packages are installed in the order they are listed.
   The installer invocations are bundled by package type (remote or local),
   meaning if you install two local packages, then two remote packages
   and then another local package, there will be two calls to ``dpkg -i ...``
   and a single call to ``apt-get install ...``.
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
   Default: ``http://deb.debian.org/debian/``
-  ``security``: The default security mirror.
   ``optional``
   Default:  ``http://security.debian.org/``
-  ``sources``: A map of additional sources that should be added to
   the aptitude sources list. The key becomes the filename in
   ``/etc/apt/sources.list.d/`` (with ``.list`` appended to it), except
   for ``main``, which designates ``/etc/apt/sources.list``.
   The value is an array with each entry being a line.
   ``optional``
-  ``components``: A list of components that should be added to the
   default apt sources. For example ``contrib`` or ``non-free``
   ``optional``
   Default: ``['main']``
-  ``trusted-keys``: List of paths (relative to the manifest) to ``.gpg`` keyrings
   that should be added to the aptitude keyring of trusted signatures for
   repositories.
   ``optional``
-  ``apt.conf.d``: A map of ``apt.conf(5)`` configuration snippets.
   The key become the filename in ``/etc/apt/apt.conf.d``, except
   ``main`` which designates ``/etc/apt/apt.conf``.
   The value is a string in the ``apt.conf(5)`` syntax.
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

Example:

.. code:: yaml

    ---
    packages:
      install:
        - /root/packages/custom_app.deb
        - puppet
      install_standard: true
      mirror: http://cloudfront.debian.net/debian
      security: http://security.debian.org/
      sources:
        puppet:
          - deb http://apt.puppetlabs.com wheezy main dependencies
      components:
        - contrib
        - non-free
      trusted-keys:
        - /root/keys/puppet.gpg
      apt.conf.d:
        00InstallRecommends: >-
          APT::Install-Recommends "false";
          APT::Install-Suggests   "false";
        00IPv4: 'Acquire::ForceIPv4 "false";'
      preferences:
        main:
          - package: *
            pin: release o=Debian, n=wheezy
            pin-priority: 800
          - package: *
            pin: release o=Debian Backports, a=wheezy-backports, n=wheezy-backports
            pin-priority: 760
          - package: puppet puppet-common
            pin: version 2.7.25-1puppetlabs1
            pin-priority: 840


Volume
~~~~~~

bootstrap-vz allows a wide range of options for configuring the disk
layout of the system. It can create unpartitioned as well as partitioned
volumes using either the gpt or msdos scheme. At most, there are only
three partitions with predefined roles configurable though. They are
boot, root and swap.

-  ``backing``: Specifies the volume backing. This setting is very
   provider specific.
   Valid values: ``ebs``, ``s3``, ``vmdk``, ``vdi``, ``raw``, ``qcow2``, ``lvm``
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
   -  ``{mount_opts}``: Options to mount the partition with. This optional
      setting overwrites the default option list bootstrap-vz would
      normally use to mount the partiton (defaults). The List is specified
      as a string array where each option/argument is an item in that array.
      ``optional`` Here some examples:
   -  ``nodev``
   -  ``nosuid``
   -  ``noexec``
   -  ``journal_ioprio=3``

   The default command used by bootstrap-vz is
   ``['mkfs.{fs}', '{device_path}']``.

   -  ``boot``: Configuration of the boot partition. All settings equal
      those of the root partition.
      ``optional``
   -  ``swap``: Configuration of the swap partition. Since the swap
      partition has its own filesystem you can only specify the size for
      this partition.
      ``optional``
   -  ``additional_path``: Configuration of additional partitions. (e.g. /var/tmp)
      All settings equal those of the root partition.


Example:

.. code:: yaml

    ---
    volume:
      backing: vdi
      partitions:
        type: msdos
        boot:
          filesystem: ext2
          size: 32MiB
        root:
          filesystem: ext4
          size: 864MiB
        swap:
          size: 128MiB

Plugins
~~~~~~~

The plugins section is a map of plugin names to whatever configuration a
plugin requires. Go to the `plugin section <../bootstrapvz/plugins>`__
of the documentation, to see the configuration for a specific plugin.


Example:

.. code:: yaml

    ---
    plugins:
      minimize_size:
        zerofree: true
        shrink: true
