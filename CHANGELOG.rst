Changelog
=========

2015-05-02
----------
Anders Ingemann:
	* Fix #32: Add image_commands example
	* Fix #99: rename image_commands to commands
	* Fix #139: Vagrant / Virtualbox provider should set ostype when 32 bits selected
	* Fix #204: Create a new phase where user modification tasks can run

2015-04-29
----------
Anders Ingemann:
	* Fix #104: Don't verify default target when adding packages
	* Fix #217: Implement get_version() function in common.tools

2015-04-28
----------
Jonh Wendell:
	* root_password: Enable SSH root login

2015-04-27
----------
John Kristensen:
	* Add authentication support to the apt proxy plugin

2015-04-25
----------
Anders Ingemann (work started 2014-08-31, merged on 2015-04-25):
	* Introduce `remote bootstrapping <bootstrapvz/remote>`__
	* Introduce `integration testing <tests/integration>`__ (for VirtualBox and EC2)
	* Merge the end-user documentation into the sphinx docs
	  (plugin & provider docs are now located in their respective folders as READMEs)
	* Include READMEs in sphinx docs and transform their links
	* Docs for integration testing
	* Document the remote bootstrapping procedure
	* Add documentation about the documentation
	* Add list of supported builds to the docs
	* Add html output to integration tests
	* Implement PR #201 by @jszwedko (bump required euca2ools version)
	* grub now works on jessie
	* extlinux is now running on jessie
	* Issue warning when specifying pre/successors across phases (but still error out if it's a conflict)
	* Add salt dependencies in the right phase
	* extlinux now works with GPT on HVM instances
	* Take @ssgelm's advice in #155 and copy the mount table -- df warnings no more
	* Generally deny installing grub on squeeze (too much of a hassle to get working, PRs welcome)
	* Add 1 sector gap between partitions on GPT
	* Add new task: DeterminKernelVersion, this can potentially fix a lot of small problems
	* Disable getty processes on jessie through logind config
	* Partition volumes by sectors instead of bytes
	  This allows for finer grained control over the partition sizes and gaps
	  Add new Sectors unit, enhance Bytes unit, add unit tests for both
	* Don't require qemu for raw volumes, use `truncate` instead
	* Fix #179: Disabling getty processes task fails half the time
	* Split grub and extlinux installs into separate modules
	* Fix extlinux config for squeeze
	* Fix #136: Make extlinux output boot messages to the serial console
	* Extend sed_i to raise Exceptions when the expected amount of replacements is not met

Jonas Bergler:
	* Fixes #145: Fix installation of vbox guest additions.

Tiago Ilieve:
	* Fixes #142: msdos partition type incorrect for swap partition (Linux)

2015-04-23
----------
Tiago Ilieve:
	* Fixes #212: Sparse file is created on the current directory

2014-11-23
----------
Noah Fontes:
	* Add support for enhanced networking on EC2 images

2014-07-12
----------
Tiago Ilieve:
	* Fixes #96: AddBackports is now a common task

2014-07-09
----------
Anders Ingemann:
	* Allow passing data into the manifest
	* Refactor logging setup to be more modular
	* Convert every JSON file to YAML
	* Convert "provider" into provider specific section

2014-07-02
----------
Vladimir Vitkov:
	* Improve grub options to work better with virtual machines

2014-06-30
----------
Tomasz Rybak:
	* Return information about created image

2014-06-22
----------
Victor Marmol:
	* Enable the memory cgroup for the Docker plugin

2014-06-19
----------
Tiago Ilieve:
	* Fixes #94: allow stable/oldstable as release name on manifest

Vladimir Vitkov:
	* Improve ami listing performance

2014-06-07
----------
Tiago Ilieve:
	* Download `gsutil` tarball to workspace instead of working directory
	* Fixes #97: remove raw disk image created by GCE after build

2014-06-06
----------
Ilya Margolin:
	* pip_install plugin

2014-05-23
----------
Tiago Ilieve:
	* Fixes #95: check if the specified APT proxy server can be reached

2014-05-04
----------
Dhananjay Balan:
	* Salt minion installation & configuration plugin
	* Expose debootstrap --include-packages and --exclude-packages options to manifest

2014-05-03
----------
Anders Ingemann:
	* Require hostname setting for vagrant plugin
	* Fixes #14: S3 images can now be bootstrapped outside EC2.
	* Added enable_agent option to puppet plugin

2014-05-02
----------
Tomasz Rybak:
	* Added Google Compute Engine Provider
