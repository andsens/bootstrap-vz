Oracle
======

The Oracle provider creates RAW images compressed in a `.tar.gz` tarball. Those image have to be uploaded using the web interface of the Oracle Compute Cloud Service dashboard.

## Quick Start

Install `apt`/`pip` dependencies:

    $ sudo apt-get install debootstrap git parted kpartx qemu-utils python-pip
    $ sudo pip install termcolor jsonschema fysom docopt pyyaml

Clone this repository:

    $ cd ~/
    $ git clone https://github.com/myhro/bootstrap-vz.git

Create a new local branch from this one:

    $ cd bootstrap-vz/
    $ git checkout -b oracle origin/oracle

Bootstrap a new image:

    $ sudo ./bootstrap-vz --debug manifests/examples/oracle/jessie.yml
