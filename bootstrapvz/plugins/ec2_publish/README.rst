EC2 publish
-----------

This plugin lets you publish an EC2 AMI to multiple regions, make AMIs public,
and output the AMIs generated in each file.

Settings
~~~~~~~~

-  ``regions``: EC2 regions to copy the final image to.
   ``optional``
-  ``public``: Whether the AMIs should be made public (i.e. available by ALL users).
   Valid values: ``true``, ``false``
   Default: ``false``.
   ``optional``
-  ``manifest_url``: URL to publish generated AMIs.
   Can be a path on the local filesystem, or a URL to S3 (https://bucket.s3-region.amazonaws.com/amis.json)
   ``optional``


