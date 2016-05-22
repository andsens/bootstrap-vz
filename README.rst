bootstrap-vz
============

bootstrap-vz is a bootstrapping framework for Debian that creates ready-to-boot
images able to run on a number of cloud providers and virtual machines.
bootstrap-vz runs without any user intervention and
generates images for the following virtualization platforms:

-  `Amazon AWS EC2 <bootstrapvz/providers/ec2>`__
   (supports both HVM and PVM; S3 and EBS backed;
   `used for official Debian images <https://wiki.debian.org/Cloud/AmazonEC2Image/Jessie>`__;
   `Quick start <#amazon-ec2-ebs-backed-ami>`__)
-  `Docker <bootstrapvz/providers/docker>`__ (`Quick start <#docker>`__)
-  `Google Compute Engine <bootstrapvz/providers/gce>`__
   (`used by Google for official Debian images <https://wiki.debian.org/Cloud/GoogleComputeEngineImage>`__)
-  `KVM <bootstrapvz/providers/kvm>`__ (Kernel-based Virtual Machine)
-  `Microsoft Azure <bootstrapvz/providers/azure>`__
-  `Oracle Compute Cloud Service <bootstrapvz/providers/oracle>`__
   (`used for official Debian images <https://wiki.debian.org/Cloud/OracleComputeImage>`__)
-  `Oracle VirtualBox <bootstrapvz/providers/virtualbox>`__ (`with Vagrant support <#virtualbox-vagrant>`__)

Its aim is to provide a reproducible bootstrapping process using
`manifests <manifests>`__
as well as supporting a high degree of customizability through plugins.

Documentation
-------------

The documentation for bootstrap-vz is available at
`bootstrap-vz.readthedocs.org <http://bootstrap-vz.readthedocs.org/en/master>`__.
There, you can discover `what the dependencies <#dependencies>`__ for
a specific cloud provider are, `see a list of available plugins <bootstrapvz/plugins>`__
and learn `how you create a manifest <manifests>`__.

Note to developers: The shared documentation links on github and readthedocs
are transformed in `a rather peculiar and nifty way`__.

__ https://github.com/andsens/bootstrap-vz/blob/master/docs/transform_github_links.py

Installation
------------

bootstrap-vz has a master branch into which stable feature branches are merged.

After checking out the branch of your choice you can install the
python dependencies by running ``python setup.py install``. However,
depending on what kind of image you'd like to bootstrap, there are
other debian package dependencies as well, at the very least you will
need ``debootstrap``.
`The documentation <http://bootstrap-vz.readthedocs.org/en/master>`__
explains this in more detail.

Note that bootstrap-vz will tell you which tools it requires when they
aren't present (the different packages are mentioned in the error
message), so you can simply run bootstrap-vz once to get a list of the
packages, install them, and then re-run.

Quick start
-----------

Here are a few quickstart tutorials for the most common images.
If you plan on partitioning your volume, you will need the ``parted``
package and ``kpartx``:

.. code-block:: sh

    root@host:~# apt-get install parted kpartx

Note that you can always abort a bootstrapping process by pressing
``Ctrl+C``, bootstrap-vz will then initiate a cleanup/rollback process,
where volumes are detached/deleted and temporary files removed, pressing
``Ctrl+C`` a second time shortcuts that procedure, halts the cleanup and
quits the process.

Docker
~~~~~~

.. code-block:: sh

    user@host:~$ sudo -i # become root
    root@host:~# git clone https://github.com/andsens/bootstrap-vz.git # Clone the repo
    root@host:~# apt-get install debootstrap python-pip docker.io # Install dependencies from aptitude
    root@host:~# pip install termcolor jsonschema fysom docopt pyyaml pyrfc3339 # Install python dependencies
    root@host:~# bootstrap-vz/bootstrap-vz bootstrap-vz/manifests/examples/docker/jessie-minimized.yml

The resulting image should be no larger than 82 MB (81.95 MB to be exact).
The manifest ``jessie-minimized.yml`` uses the
`minimize\_size <bootstrapvz/plugins/minimize_size>`__ plugin to reduce the image
size considerably. Rather than installing docker from the debian main repo
it is recommended to install `the latest docker version <https://docs.docker.com/engine/installation/debian/#debian-jessie-80-64-bit>`__.


VirtualBox Vagrant
~~~~~~~~~~~~~~~~~~

.. code-block:: sh

    user@host:~$ sudo -i # become root
    root@host:~# git clone https://github.com/andsens/bootstrap-vz.git # Clone the repo
    root@host:~# apt-get install qemu-utils debootstrap python-pip # Install dependencies from aptitude
    root@host:~# pip install termcolor jsonschema fysom docopt pyyaml # Install python dependencies
    root@host:~# modprobe nbd max_part=16
    root@host:~# bootstrap-vz/bootstrap-vz bootstrap-vz/manifests/examples/virtualbox/jessie-vagrant.yml

(The `modprobe nbd max_part=16` part enables the network block device driver to support up to 16 partitions
on a device)

If you want to use the `minimize\_size <bootstrapvz/plugins/minimize_size>`__ plugin,
you will have to install the ``zerofree`` package and `VMWare Workstation`__ as well.

__ https://my.vmware.com/web/vmware/info/slug/desktop_end_user_computing/vmware_workstation/10_0

Amazon EC2 EBS backed AMI
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sh

    user@host:~$ sudo -i # become root
    root@host:~# git clone https://github.com/andsens/bootstrap-vz.git # Clone the repo
    root@host:~# apt-get install debootstrap python-pip # Install dependencies from aptitude
    root@host:~# pip install termcolor jsonschema fysom docopt pyyaml boto # Install python dependencies
    root@host:~# bootstrap-vz/bootstrap-vz bootstrap-vz/manifests/official/ec2/ebs-jessie-amd64-hvm.yml

To bootstrap S3 backed AMIs, bootstrap-vz will also need the
``euca2ools`` package. However, version 3.2.0 is required meaning you
must install it directly from the eucalyptus repository like this:

.. code-block:: sh

    apt-get install --no-install-recommends python-dev libxml2-dev libxslt-dev gcc zlib1g-dev
    pip install git+git://github.com/eucalyptus/euca2ools.git@v3.2.0

Cleanup
-------

bootstrap-vz tries very hard to clean up after itself both if a run was
successful but also if it failed. This ensures that you are not left
with volumes still attached to the host which are useless. If an error
occurred you can simply correct the problem that caused it and rerun
everything, there will be no leftovers from the previous run (as always
there are of course rare/unlikely exceptions to that rule). The error
messages should always give you a strong hint at what is wrong, if that
is not the case please consider `opening an issue`__ and attach
both the error message and your manifest (preferably as a gist or
similar).

__ https://github.com/andsens/bootstrap-vz/issues

Dependencies
------------

bootstrap-vz has a number of dependencies depending on the target
platform and `the selected plugins <bootstrapvz/plugins>`__.
At a bare minimum the following python libraries are needed:

* `termcolor <https://pypi.python.org/pypi/termcolor>`__
* `fysom <https://pypi.python.org/pypi/fysom>`__
* `jsonschema <https://pypi.python.org/pypi/jsonschema>`__
* `docopt <https://pypi.python.org/pypi/docopt>`__
* `pyyaml <https://pypi.python.org/pypi/pyyaml>`__

To bootstrap Debian itself `debootstrap`__ is needed as well.

__ https://packages.debian.org/wheezy/debootstrap

Any other requirements are dependent upon the manifest configuration
and are detailed in the corresponding sections of the documentation.
Before the bootstrapping process begins however,
bootstrap-vz will warn you if a requirement has not been met.

Developers
----------

The API documentation, development guidelines and an explanation of
bootstrap-vz internals can be found at `bootstrap-vz.readthedocs.org`__.

__ http://bootstrap-vz.readthedocs.org/en/master/developers

Contributing
------------

Contribution guidelines are described in the documentation under `Contributing <CONTRIBUTING.rst>`__.
There's also a topic regarding `the coding style <CONTRIBUTING.rst#coding-style>`__.

Before bootstrap-vz
-------------------

bootstrap-vz was coded from scratch in python once the bash script
architecture that was used in the
`build-debian-cloud <https://github.com/andsens/build-debian-cloud>`__
bootstrapper reached its limits. The project has since grown well beyond
its original goal, but has kept the focus on Debian images.
