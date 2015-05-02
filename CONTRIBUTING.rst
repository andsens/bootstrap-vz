Contributing
============


Sending pull requests
---------------------
Do you want to contribute to the bootstrap-vz project? Nice! Here is the basic workflow:

* Read the `development guidelines <#development-guidelines>`__
* Fork this repository.
* Make any changes you want/need.
* Check the coding style of your changes using `tox <http://tox.readthedocs.org/>`__ by running `tox -e flake8`
  and fix any warnings that may appear.
  This check will be repeated by `Travis CI <https://travis-ci.org/andsens/bootstrap-vz>`__
  once you send a pull request, so it's better if you check this beforehand.
* If the change is significant (e.g. a new plugin, manifest setting or security fix)
  add your name and contribution to the `changelog <CHANGELOG.rst>`__.
* Commit your changes.
* Squash the commits if needed. For instance, it is fine if you have multiple commits describing atomic units
  of work, but there's no reason to have many little commits just because of corrected typos.
* Push to your fork, preferably on a topic branch.
* Send a pull request to the `master` branch.

Please try to be very descriptive about your changes when you write a pull request, stating what it does, why
it is needed, which use cases this change covers, etc.
You may be asked to rebase your work on the current branch state, so it can be merged cleanly.
If you push a new commit to your pull request you will have to add a new comment to the PR,
provided that you want us notified. Github will otherwise not send a notification.

Be aware that your modifications need to be properly documented. Please take a look at the
`documentation section <#documentation>`__ to see how to do that.

Happy hacking! :-)


Development guidelines
----------------------

The following guidelines should serve as general advice when
developing providers or plugins for bootstrap-vz. Keep in mind that
these guidelines are not rules , they are advice on how to better add
value to the bootstrap-vz codebase.


The manifest should always fully describe the resulting image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The outcome of a bootstrapping process should never depend on settings
specified elsewhere.

This allows others to easily reproduce any setup other people are running
and makes it possible to share manifests.
`The official debian EC2 images`__ for example can be reproduced
using the manifests available in the manifest directory of bootstrap-vz.

__ https:/aws.amazon.com/marketplace/seller-profile?id=890be55d-32d8-4bc8-9042-2b4fd83064d5

The bootstrapper should always be able to run fully unattended
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For end users, this guideline minimizes the risk of errors. Any
required input would also be in direct conflict with the previous
guideline that the manifest should always fully describe the resulting
image.

Additionally developers may have to run the bootstrap
process multiple times though, any prompts in the middle of that
process may significantly slow down the development speed.


The bootstrapper should only need as much setup as the manifest requires
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Having to shuffle specific paths on the host into place
(e.g. ``/target`` has to be created manually) to get the bootstrapper
running is going to increase the rate of errors made by users.
Aim for minimal setup.

Exceptions are of course things such as the path to
the VirtualBox Guest Additions ISO or tools like ``parted`` that
need to be installed on the host.


Roll complexity into which tasks are added to the tasklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If a ``run()`` function checks whether it should do any work or simply be
skipped, consider doing that check in ``resolve_tasks()`` instead and
avoid adding that task alltogether. This allows people looking at the
tasklist in the logfile to determine what work has been performed.

If a task says it will modify a file but then bails , a developer may get
confused when looking at that file after bootstrapping. He could
conclude that the file has either been overwritten or that the
search & replace does not work correctly.


Control flow should be directed from the task graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Avoid creating complicated ``run()`` functions. If necessary, split up
a function into two semantically separate tasks.

This allows other tasks to interleave with the control-flow and add extended
functionality (e.g. because volume creation and mounting are two
separate tasks, `the prebootstrapped plugin
<bootstrapvz/plugins/prebootstrapped>`__
can replace the volume creation task with a task of its own that
creates a volume from a snapshot instead, but still reuse the mount task).


Task classes should be treated as decorated run() functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tasks should not have any state, thats what the
BootstrapInformation object is for.

Only add stuff to the BootstrapInformation object when really necessary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is mainly to avoid clutter.


Use a json-schema to check for allowed settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The json-schema may be verbose but it keeps the bulk of check work outside the
python code, which is a big plus when it comes to readability.
This only applies bas long as the checks are simple.
You can of course fall back to doing the check in python when that solution is
considerably less complex.


When invoking external programs, use long options whenever possible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This makes the commands a lot easier to understand, since
the option names usually hint at what they do.


When invoking external programs, don't use full paths, rely on ``$PATH``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This increases robustness when executable locations change.
Example: Use ``log_call(['wget', ...])`` instead of ``log_call(['/usr/bin/wget', ...])``.


Coding style
------------
bootstrap-vz is coded to comply closely with the PEP8 style
guidelines. There however a few exceptions:

* Max line length is 110 chars, not 80.
* Multiple assignments may be aligned with spaces so that the = match
  vertically.
* Ignore ``E101``: Indent with tabs and align with spaces
* Ignore ``E221 & E241``: Alignment of assignments
* Ignore ``E501``: The max line length is not 80 characters
* Ignore ``W191``: Indent with tabs not spaces

The codebase can be checked for any violations quite easily, since those rules are already specified in the
`tox <http://tox.readthedocs.org/>`__ configuration file.
::

    tox -e flake8


Documentation
-------------
When developing a provider or plugin, make sure to update/create the README.rst
located in provider/plugin folder.
Any links to other rst files should be relative and work, when viewed on github.
For information on `how to build the documentation <docs#building>`_ and how
the various parts fit together,
refer to `the documentation about the documentation <docs>`__ :-)
