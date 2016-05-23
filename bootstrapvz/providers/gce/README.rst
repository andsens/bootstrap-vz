Google Compute Engine
=====================

The `GCE <https://cloud.google.com/products/compute-engine/>`__ provider
can creates image as expected by GCE - i.e. raw disk image in \*.tar.gz
file. It can upload created images to Google Cloud Storage (to a URI
provided in the manifest by ``gcs_destination``) and can register images to
be used by Google Compute Engine to a project provided in the manifest by
``gce_project``. Both of those functionalities are not fully tested yet.

Note that to register an image, it must first be uploaded to GCS, so you must
specify ``gcs_destination`` (upload to GCS) to use ``gce_project`` (register
with GCE)

Manifest settings
-----------------

Provider
~~~~~~~~

-  ``description``: Description of the image.
-  ``gcs_destination``: Image destination in GCS.
-  ``gce_project``: GCE project in which to register the image.


Example:

.. code-block:: yaml

    ---
    provider:
      name: gce
      description: Debian {system.release} {system.architecture}
      gcs_destination: gs://my-bucket
      gce_project: my-project
