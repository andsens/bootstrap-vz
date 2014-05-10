Contributing
============

Do you want to contribute to the bootstrap-vz project? Nice! Here is the basic workflow:

* Read the [development guidelines](http://bootstrap-vz.readthedocs.org/en/master/guidelines.html)
* Fork this repository.
* Make any changes you want/need.
* Check the coding style of your changes using [tox](http://tox.readthedocs.org/) by running `tox -e flake8`
  and fix any warnings that may appear.
  This check will be repeated by [Travis CI](https://travis-ci.org/andsens/bootstrap-vz)
  once you send a pull request, so it's better if you check this beforehand.
* If the change is significant (e.g. a new plugin, manifest setting or security fix)
  add your name and contribution to the [CHANGELOG](CHANGELOG).
* Commit your changes.
* Squash the commits if needed. For instance, it is fine if you have multiple commits describing atomic units
  of work, but there's no reason to have many little commits just because of corrected typos.
* Push to your fork, preferably on a topic branch.

From here on there are two paths to consider:

If your patch is a new feature, e.g.: plugin, provider, etc. then:

* Send a pull request to the `development` branch. It will be merged into the `master` branch when we can make
  sure that the code is stable.

If it is a bug/security fix:

* Send a pull request to the `master` branch.

--

Please try to be very descriptive about your changes when you write a pull request, stating what it does, why
it is needed, which use cases this change covers etc.
You may be asked to rebase your work on the current branch state, so it can be merged cleanly.
If you push a new commit to your pull request you will have to add a new comment to the PR,
provided that you want us notified. Github will otherwise not send a notification.

Be aware that your modifications need to be properly documented and pushed to the `gh-pages` branch, if they
concern anything done on `master`. Otherwise, they should be sent to the `gh-pages-dev`.

Happy hacking! :-)
