Official GCE manifests
======================

These are the official manifests used to build [Google Compute Engine (GCE) Debian images](https://cloud.google.com/compute/docs/images).

The included packages and configuration changes are necessary for Debian to run on GCE as a first class citizen of the platform.
Included GCE software is published on github: [Google Compute Engine guest environment](https://github.com/GoogleCloudPlatform/compute-image-packages)

Debian 8 Package Notes:

* python-crcmod is pulled in from backports as it provides a compiled crcmod required for the Google Cloud Storage CLI (gsutil).
* cloud-utils and cloud-guest-utils are pulled in from backports as they provide a fixed version of growpart to safely grow the root partition on disks >2TB.

Debian 8 and 9 Package Notes:

* google-cloud-sdk is pulled from a Google Cloud repository.
* google-compute-engine is pulled from a Google Cloud repository.
* python-google-compute-engine is pulled from a Google Cloud repository.
* python3-google-compute-engine is pulled from a Google Cloud repository.

jessie-minimal and stretch-minimal:

The only additions are the necessary google-compute-engine, python-google-compute-engine, and python3-google-compute-engine packages. This image is not published on GCE however the manifest is provided here for those wishing a minimal GCE Debian image.

Deprecated manifests:

Debian 7 Wheezy and Backports Debian 7 Wheezy are deprecated images on GCE and are no longer supported. These manifests are provided here for historic purposes.
