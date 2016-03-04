File copy
---------

This plugin lets you copy files from the host to the VM under construction,
create directories, and set permissions and ownership.

Note that this necessarily violates the `first development guideline`_.

.. _first development guideline: https://github.com/andsens/bootstrap-vz/blob/master/CONTRIBUTING.rst#the-manifest-should-always-fully-describe-the-resulting-image


Settings
~~~~~~~~

The ``file_copy`` plugin takes a (non-empty) ``files`` list, and optionnaly a ``mkdirs`` list.

Files (items in the ``files`` list) must be objects with the following properties:

-  ``src`` and ``dst`` (required) are the source and destination paths.
   ``src`` is relative to the current directory, whereas ``dst`` is a path in the VM.
-  ``permissions`` (optional) is a permission string in a format appropriate for ``chmod(1)``.
-  ``owner`` and ``group`` (optional) are respectively a user and group specification,
   in a format appropriate for ``chown(1)`` and ``chgrp(1)``.

Folders (items in the ``mkdirs`` list) must be objects with the following properties:
-  ``dir`` (required) is the path of the directory.
-  ``permissions``, ``owner`` and ``group`` are the same as for files.
