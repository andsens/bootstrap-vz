bootstrap-vz
===========================================
bootstrap-vz is a bootstrapping framework for Debian.
It is is specifically targeted at bootstrapping systems for virtualized environments.
bootstrap-vz runs without any user intervention and generates ready-to-boot images for
[a number of virtualization platforms](http://andsens.github.io/bootstrap-vz/providers.html).
Its aim is to provide a reproducable bootstrapping process using [manifests](http://andsens.github.io/bootstrap-vz/manifest.html) as well as supporting a high degree of customizability through plugins.

bootstrap-vz was coded from scratch in python once the bash script architecture that was used in the
[build-debian-cloud](https://github.com/andsens/build-debian-cloud) bootstrapper reached its
limits.

Documentation
-------------
The end-user documentation for bootstrap-vz is available
at [andsens.github.io/bootstrap-vz](http://andsens.github.io/bootstrap-vz).
There, you can discover [what the dependencies](http://andsens.github.io/bootstrap-vz/#dependencies)
for a specific cloud provider are, [see a list of available plugins](http://andsens.github.io/bootstrap-vz/plugins.html)
and learn [how you create a manifest](http://andsens.github.io/bootstrap-vz/manifest.html).

Installation
------------

bootstrap-vz has a master branch for stable releases and a development for, well, development.  
After checking out the branch of your choice you can install the python dependencies by running
`python setup.py install`. However, depending on what kind of image you'd like to bootstrap,
there are other debian package dependencies as well, at the very least you will need `debootstrap`.  
[The documentation](http://andsens.github.io/bootstrap-vz/) explains this in more detail.

Note that bootstrap-vz will tell you which tools it requires when they aren't
present (the different packages are mentioned in the error message), so you can
simply run bootstrap-vz once to get a list of the packages, install them,
and then re-run.

Developers
----------
The API documentation, development guidelines and an explanation of bootstrap-vz internals
can be found at [bootstrap-vz.readthedocs.org](http://bootstrap-vz.readthedocs.org).

Contributing
------------

Contribution guidelines are described on the [CONTRIBUTING](CONTRIBUTING.md) file. There's also a
[topic on the documentation](http://bootstrap-vz.readthedocs.org/en/development/guidelines.html#coding-style)
regarding the coding style.
