System tests
============
`System tests`__ test
bootstrap-vz in its entirety.
This testing includes building images from manifests and
creating/booting said images.

__ http://en.wikipedia.org/wiki/System_testing

Since hardcoding manifests for each test, bootstrapping them and booting the
resulting images is too much code for a single test, a testing harness has
been developed that reduces each test to it's bare essentials:

* Combine available `manifest partials <#manifest-partials>`__ into a single manifest
* Boot an instance from a manifest
* Run tests on the booted instance

In order for the system testing harness to be able to bootstrap it must
know about your `build-servers <../../bootstrapvz/remote#build-servers-yml>`__.
Depending on the manifest that is bootstrapped, the harness chooses
a fitting build-server, connects to it and starts the bootstrapping process.

When running system tests, the framework will look for ``build-servers.yml``
at the root of the repo and raise an error if it is not found.


Manifest combinations
---------------------
The tests mainly focus on varying key parts of an image
(e.g. partitioning, Debian release, bootloader, ec2 backing, ec2 virtualization method)
that have been problem areas.
Essentially the tests are the cartesian product of these key parts.


Aborting a test
---------------
You can press ``Ctrl+C`` at any time during the testing to abort -
the harness will automatically clean up any temporary resources and shut down
running instances. Pressing ``Ctrl+C`` a second time stops the cleanup and quits
immediately.


Manifest partials
-----------------
Instead of creating manifests from scratch for each single test, reusable parts
are factored out into partials in the manifest folder.
This allows code like this:

.. code-block:: python

	partials = {'vdi': '{provider: {name: virtualbox}, volume: {backing: vdi}}',
	            'vmdk': '{provider: {name: virtualbox}, volume: {backing: vmdk}}',
	            }

	def test_unpartitioned_extlinux_oldstable():
		std_partials = ['base', 'stable64', 'extlinux', 'unpartitioned', 'root_password']
		custom_partials = [partials['vmdk']]
		manifest_data = merge_manifest_data(std_partials, custom_partials)

The code above produces a manifest for Debian stable 64-bit unpartitioned
virtualbox VMDK image.
``root_password`` is a special partial in that the actual password is
randomly generated on load.


Missing parts
-------------
The system testing harness is in no way complete.

* It still has no support for providers other than Virtualbox, EC2 and Docker.
* Creating an SSH connection to a booted instance is cumbersome and does not
  happen in any of the tests - this would be particularly useful when manifests
  are to be tested beyond whether they boot up.
