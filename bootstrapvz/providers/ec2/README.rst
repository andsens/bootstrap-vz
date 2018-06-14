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
run). Set the variable ``install_init_scripts`` to ``False`` in order
to disable this behaviour.

Manifest settings
-----------------

Credentials
~~~~~~~~~~~

The AWS credentials can be configured via the manifest or through
environment variables. If using EBS backing, credentials can not be included to
allow `boto3 <http://boto3.readthedocs.io/en/latest/guide/configuration.html>`__
to discover it's credentials. To bootstrap S3 backed instances you will
need a user certificate and a private key in addition to the access key
and secret key, which are needed for bootstraping EBS backed instances.

The settings describes below should be placed in the ``credentials`` key
under the ``provider`` section.

-  ``access-key``: AWS access-key.
   May also be supplied via the environment variable
   ``$AWS_ACCESS_KEY``
   ``required for S3 backing``
-  ``secret-key``: AWS secret-key.
   May also be supplied via the environment variable
   ``$AWS_SECRET_KEY``
   ``required for S3 backing``
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

.. code-block:: yaml

    ---
    provider:
      name: ec2
      credentials:
        access-key: AFAKEACCESSKEYFORAWS
        secret-key: thes3cr3tkeyf0ryourawsaccount/FS4d8Qdva

Profile
~~~~~~~
A profile from the `boto3 shared credentials files <http://boto3.readthedocs.io/en/latest/guide/configuration.html#shared-credentials-file>`__
can be declared rather than needing to enter credentials into the
manifest.

-  ``profile``: AWS configuration profile.

Example:

.. code-block:: yaml

    ---
    provider:
      name: ec2
      credentials:
        profile: Default

Virtualization
~~~~~~~~~~~~~~

EC2 supports both paravirtual and hardware virtual machines.
The virtualization type determines various factors about the
virtual machine performance (read more about this `in the EC2 docs`__).

__ http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/virtualization_types.html

-  ``virtualization``: The virtualization type
   Valid values: ``pvm``, ``hvm``
   ``required``


Example:

.. code-block:: yaml

    ---
    provider:
      name: ec2
      virtualization: hvm

Enhanced networking
~~~~~~~~~~~~~~~~~~~

Install enhanced networking drivers to take advantage of SR-IOV
capabilities on hardware virtual machines.
Read more about this in `the EC2 docs`__.

__ http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enhanced-networking.html

Example:

.. code-block:: yaml

    ---
    provider:
      name: ec2
      virtualization: hvm
      enhanced_networking: simple

Amazon Drivers
~~~~~~~~~~~~~~

Define the version for the Amazon Elastic Network
Adapter (ENA) driver.
Read more about this on the `Amazon Drivers git repo`__.

__ https://github.com/amzn/amzn-drivers

-  ``amzn-driver-version``: Default: master
   Valid values: ``master``, ``#.#.#``
   ``optional``

Example:

.. code-block:: yaml

    ---
    provider:
      name: ec2
      amzn-driver-version: 1.5.0

Encrypted volumes
~~~~~~~~~~~~~~~~~

Encrypted AMIs that can be used to launch instances with encrypted boot volume
are supported. Defining encryption key is optional and EC2 uses default
encryption key if one is not set. Encryption works only with EBS volumes.

- ``encrypted:``: Default: False
  Valid values: ``True``, ``False``
  ``optional``
- ``kms_key_id:``: Default: EC2 default EBS encryption key
  Valid values: arn of the KMS key
  ``optional``

Example:

.. code-block:: yaml

    ---
    provider:
      name: ec2
      encrypted: True
      kms_key_id: arn:aws:kms:us-east-1:1234567890:key/00000000-0000-0000-0000-000000000000

Image
~~~~~

-  ``description``: Description of the AMI.
   ``manifest vars``
-  ``bucket``: When bootstrapping an S3 backed image, this
   will be the bucket where the image is uploaded to.
   ``required for S3 backing``
-  ``region``: Region in which the AMI should be registered.
   ``required for S3 backing``

Example:

.. code-block:: yaml

    ---
    provider:
      name: ec2
      description: Debian {system.release} {system.architecture}
      bucket: debian-amis
      region: us-west-1


Tags
~~~~

EBS volumes, snapshots and AMIs are tagged using AWS resource tags
with the tag names and values defined in the manifest. Tags can be used to
categorize AWS resources, e.g. by purpose or environment. They can also be
used to limit access to resources using `IAM policies`__.

__ https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_ec2_ebs-owner.html

Example:

.. code-block:: yaml

    ---
    tags:
      Name: "Stretch 9.0 alpha"
      Debian: "9.0~{%Y}{%m}{%d}{%H}{%M}"
      Role: "test"

Restrictions on tag names and values are defined in `EC2 docs`__.

__ https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html#tag-restrictions


Dependencies
------------

To communicate with the AWS API `boto3 <https://github.com/boto/boto>`__
is required you can install boto with
``pip install boto3`` (on wheezy, the packaged version is too low). S3
images are chopped up and uploaded using
`euca2ools <https://github.com/eucalyptus/euca2ools>`__ (install with
``apt-get install euca2ools``).
