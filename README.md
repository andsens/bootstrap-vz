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

Developers
----------
The API documentation can be found at [bootstrap-vz.readthedocs.org](http://bootstrap-vz.readthedocs.org).
