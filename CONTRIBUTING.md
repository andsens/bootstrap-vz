Contributing
============

Do you want to contribute to the bootstrap-vz project? Nice! Here is the basic workflow:

* Fork this repository.
* Make any changes you want/need.
* Check the coding style of your changes using [tox](http://tox.readthedocs.org/), running `tox -e flake8` and
fixing any warnings that may appear. This will be done again by
[Travis CI](https://travis-ci.org/andsens/bootstrap-vz) later when you send a pull request, so it's better if
you check this before.
* Commit your changes.
* Squash the commits if needed. For instance, it is fine if you have multiple commits describing atomic units
of work, but there's no reason to have many little commits just because of corrected typos.
* Push to your fork, preferable on a topic branch.

By this moment, there are two paths that you have to consider:

If you patch is a new feature, e.g.: plugin, provider, etc. then:

* Send a pull request to the `development` branch. It will be merged into the `master` branch when we can make
sure that the code is stable.

If it is a bug/security fix:

* Send a pull request to the `master` branch.

Please try to be very descriptive about your changes when you write a pull request, stating what it does, why
it is needed, what use cases do you think it would be useful, etc. You could as well be asked to rebase your
work on the current branch state, so it can be merged cleanly. Also, be in mind that if you push a new commit
to your pull request, we won't be notified just by this - that will happen only if you make a new comment on
the issue.

Be aware that your modifications needs to be properly documented and pushed to the `gh-pages` branch, if they
concern anything done on `master`. Otherwise, they should be sent to the `gh-pages-dev`.

Happy hacking! :-)
