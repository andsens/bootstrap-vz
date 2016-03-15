Google Compute Engine
=====================

The `GCE <https://cloud.google.com/products/compute-engine/>`__ provider
can creates image as expected by GCE - i.e. raw disk image in \*.tar.gz
file. It can upload created images to Google Storage Engine (to URI
provided in manifest by ``gcs_destination``) and can register image to
be used by Google Compute Engine to project provided in manifest by
``gce_project``. Both of those functionalities are not fully tested yet.

Manifest settings
-----------------

Provider
~~~~~~~~

-  ``description``: Description of the image.
-  ``gcs_destination``: Image destination in GSE.
-  ``gce_project``: GCE project in which to register the image.


Example:

.. code-block:: yaml

    ---
    provider:
      name: gce
      description: Debian {system.release} {system.architecture}
      gcs_destination: gs://my-bucket
      gce_project: my-project
