build-debian-cloud python version (preview)
===========================================

This is a preview of the build-debian-cloud python version.  
It currently only supports EBS booted volumes and none of the plugins have been ported.

Suggestions
-----------
The reason I release this preview is to get as many suggestions as possible.
If you have an idea for how to improve upon the architecture or
simply spotted a bug, please feel free to file a bug report.
Pull requests are also welcome!

Dependencies
------------
You will need to run debian wheezy with python 2.7 and debootstrap installed.
Also the following python libraries are required:
* boto
* jsomschema (version 4, only available through pip)
* termcolor

Highlights
----------
* The desired image is configured entirely via a JSON manifest file
	* Manifests are validated by a json schemas
	* Support comments
* Proper support for different providers
* The task based system has been completely revamped
	* Higher granularity increases reusability of tasks across providers
	* Tasks are neatly organized into modules
	* A task dependency graph is built to determine the execution order
* Support for rollback actions if something fails
* Logfiles
	* All output from invoked subprocesses is logged

Disclaimer
----------
This is only a preview of the bootstrapper, so you can expect bugs and major architectural changes.
Do not expect that the final version will look anything like this.
