EC2
===

The `EC2 <http://aws.amazon.com/ec2/>`__ provider automatically creates
a volume for bootstrapping (be it EBS or S3), makes a snapshot of it
once it is done and registers it as an AMI. EBS volume backing only
works on an EC2 host while S3 backed volumes *should* work locally (at
this time however they do not, a fix is in the works).

Unless `the cloud-init plugin <../../plugins/cloud_init>`__
is used, special startup scripts will be installed that automatically fetch the
configured authorized\_key from the instance metadata and save or run
any userdata supplied (if the userdata begins with ``#!`` it will be
run).

Credentials
-----------

The AWS credentials can be configured in two ways: Via the manifest or
through environment variables. To bootstrap S3 backed instances you will
need a user certificate and a private key in addition to the access key
and secret key, which are needed for bootstraping EBS backed instances.

The settings describes below should be placed in the ``credentials`` key
under the ``provider`` section.

-  ``access-key``: AWS access-key.
   May also be supplied via the environment variable
   ``$AWS_ACCESS_KEY``
   ``required for EBS & S3 backing``
-  ``secret-key``: AWS secret-key.
   May also be supplied via the environment variable
   ``$AWS_SECRET_KEY``
   ``required for EBS & S3 backing``
-  ``certificate``: Path to the AWS user certificate. Used for
   uploading the image to an S3 bucket.
   May also be supplied via the environment variable
   ``$AWS_CERTIFICATE``
   ``required for S3 backing``
-  ``private-key``: Path to the AWS private key. Used for uploading
   the image to an S3 bucket.
   May also be supplied via the environment variable
   ``$AWS_PRIVATE_KEY``
   ``required for S3 backing``
-  ``user-id``: AWS user ID. Used for uploading the image to an S3
   bucket.
   May also be supplied via the environment variable ``$AWS_USER_ID``
   ``required for S3 backing``

Example:

.. code:: yaml

    ---
    provider:
      name: ec2
      virtualization: hvm
      enhanced_networking: simple
      credentials:
        access-key: AFAKEACCESSKEYFORAWS
        secret-key: thes3cr3tkeyf0ryourawsaccount/FS4d8Qdva

Dependencies
------------

To communicate with the AWS API `boto <https://github.com/boto/boto>`__
is required (version 2.14.0 or higher) you can install boto with
``pip install boto`` (on wheezy, the packaged version is too low). S3
images are chopped up and uploaded using
`euca2ools <https://github.com/eucalyptus/euca2ools>`__ (install with
``apt-get install euca2ools``).
