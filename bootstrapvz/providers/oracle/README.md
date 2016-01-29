Oracle
======

The Oracle provider creates RAW images compressed in a `.tar.gz` tarball. Those image have to be uploaded using the web interface of the Oracle Compute Cloud Service dashboard.

## Dependencies

Oracle Compute Cloud currently supports only kernel images compressed with GZIP. Debian kernels from 3.6 and up are compressed with XZ and will not work. If you plan to bootstrap a `jessie` image, for instance, you will have to download or build a custom kernel. The manifest examples expects a custom kernel package located at `/tmp/linux-image-3.16.7-ckt11-gzip-1_amd64.deb`.

## Quick Start

Install `apt`/`pip` dependencies:

    $ sudo apt-get install debootstrap git parted kpartx qemu-utils python-pip
    $ sudo pip install termcolor jsonschema fysom docopt pyyaml

Download a custom-built gzipped kernel:

    $ cd /tmp/
    $ wget http://viridian.ilieve.org/kernel/linux-image-3.16.7-ckt11-gzip-1_amd64.deb

Clone this repository:

    $ cd ~/
    $ git clone https://github.com/myhro/bootstrap-vz.git

Create a new local branch from this one:

    $ cd bootstrap-vz/
    $ git checkout -b oracle origin/oracle

Bootstrap a new image:

    $ sudo ./bootstrap-vz --debug manifests/examples/oracle/jessie.yml
