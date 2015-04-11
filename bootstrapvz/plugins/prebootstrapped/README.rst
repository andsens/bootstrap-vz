prebootstrapped
---------------

When developing for bootstrap-vz, testing can be quite tedious since the
bootstrapping process can take a while. The prebootstrapped plugin
solves that problem by creating a snapshot of your volume right after
all the software has been installed. The next time bootstrap-vz is run,
the plugin replaces all volume preparation and bootstrapping tasks and
recreates the volume from the snapshot instead.

The plugin assumes that the users knows what he is doing (e.g. it
doesn't check whether bootstrap-vz is being run with a partitioned
volume configuration, while the snapshot is unpartitioned).

When no snapshot or image is specified the plugin creates one and
outputs its ID/path. Specifying an ID/path enables the second mode of
operation which recreates the volume from the specified snapshot instead
of creating it from scratch.

Settings
~~~~~~~~

-  ``snapshot``: ID of the EBS snapshot to use. This setting only works
   with EBS backed EC2 configurations.
-  ``image``: Path to the loopbackvolume snapshot. This setting works
   with all configurable volume backings except EBS.
