Puppet
------

Installs `puppet version 4 <http://puppetlabs.com/>` PC1 From the site 
repository `<http://apt.puppetlabs.com/>` and optionally applies a
manifest inside the chroot. You can also have it copy your puppet
configuration into the image so it is readily available once the image
is booted.

Rationale and use case in a masterless setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You want to use this plugin when you wish to create an image and to be able to
manage that image with Puppet. You have a Puppet 4 setup in mind and thus you 
want the image to contain the puppet agent software from the puppetlabs repo. 
You want it to almost contain everything you need to get it up and running 
This plugin does just that!
While you're at it, throw in some modules from the forge as well!
Want to include your own modules? Include them as assets!

This is primarily useful when you have a very limited collection of nodes you 
wish to manage with puppet without to having to set up an entire puppet infra-
structure. This allows you thus to work "masterless". 

You can use this to bootstrap any kind of appliance, like a puppet master!
 
For now this plugin is only compatible with Debian versions Wheezy, Jessie and 
Stretch. These are Debian distributions supported by puppetlabs.

About Master/agent setups
~~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to use this plugin in an infrastructure where a puppet master is 
present, you should evaluate what your setup is. In a puppet OSS server setup 
it can be useful to just use the plugin without any manifests, assets or 
modules included. 
In a puppet PE environment you will probably not need this plugin since the PE 
server console gives you an URL that installs the agent corresponding to your 
PE server. 

About Puppet 5
~~~~~~~~~~~~~~

Although Puppet 5 is available for some time, there is still heavy development 
going on in that version. This module does NOT support the installation of this
version at this time. If you think this should be the case, please open up an 
issue on `<https://github.com/NeatNerdPrime/bootstrap-vz/>`.

Settings
~~~~~~~~

-  ``manifest``: Path to the puppet manifest that should be applied.
   ``optional``
-  ``assets``: Path to puppet assets. The contents will be copied into
   ``/etc/puppetlabs`` on the image. Any existing files will be overwritten.
   ``optional``
-  ``install_modules``: A list of modules you wish to install available from 
   `<https://forge.puppetlabs.com/>` inside the chroot. It will assume a FORCED
   install of the modules.
   This list is a list of tuples. Every tuple must at least contain the module 
   name. A version is optional, when no version is given, it will take the 
   latest version available from the forge. 
   Format: [module_name (required), version (optional)]
-  ``enable_agent``: Whether the puppet agent daemon should be enabled. 
   ``optional - not recommended``. disabled by default. UNTESTED
   
An example bootstrap-vz manifest is included in the ``KVM`` folder of the 
manifests examples directory.
      
Limitations
~~~~~~~~~~~
(Help is always welcome, feel free to chip in!)
General:

- This plugin only installs the PC1 package for now, needs to be extended to 
  be able to install the package of choice

Manifests:

- Running puppet manifests is not recommended and untested, see below

Assets:

- The assets path must be ABSOLUTE to your manifest file.  

install_modules:

- It assumes installing the given list of tuples of modules with the following 
  command: 
  "... install --force $module_name (--version $version_number)"
  The module name is mandatory, the version is optional. When no version is 
  given, it  will pick the master version of the
  module from `<https://forge.puppetlabs.com/>`
- It assumes the modules are installed into the "production" environment. 
  Installing into another environment e.g. develop, is currently not 
  implemented.
- You cannot include local modules this way, to include you homebrewn modules,
  You need to inject them through the assets directive.

UNTESTED:

- Enabling the agent and applying the manifest inside the chrooted environment.
	Keep in mind that when applying a manifest when enabling the agent option,
	the system is in a chrooted environment. This can prevent daemons from 
	running	properly (e.g. listening to ports), they will also need to be shut 
	down gracefully (which bootstrap-vz cannot do) before unmounting the 
	volume. It is advisable to avoid starting any daemons inside the chroot at 
	all.
