bootstrap-vz
===========================================

bootstrap-vz is a bootstrapping framework for Debian.
It is is specifically intended to bootstrap systems for virtualized environments.
It runs without any user intervention and generates ready-to-boot images for
[a number of virtualization platforms(http://andsens.github.io/bootstrap-vz/providers.html).
Its aim is to provide a reproducable bootstrapping process using <a href="manifest.html">manifests</a>
as well as supporting a high degree of customizability through plugins.<br/>
bootstrap-vz was coded from scratch in python once the bash scripts that were used in the
[build-debian-cloud](https://github.com/andsens/build-debian-cloud) bootstrapper reached their
limits.

Documentation
-------------
The documentation for bootstrap-vz is available
at [andsens.github.io/bootstrap-vz](http://andsens.github.io/bootstrap-vz).
There, you can discover [what the dependencies](http://andsens.github.io/bootstrap-vz/#dependencies)
for a specific cloud provider are, [see the list of available plugins](http://andsens.github.io/bootstrap-vz/plugins.html)
and learn [how you create a manifest](http://andsens.github.io/bootstrap-vz/manifest.html).
