Commands
--------------

This plugin allows you to run arbitrary commands during the bootstrap process.
The commands are run at an indeterminate point *after* packages have been
installed, but *before* the volume has been unmounted.

Settings
~~~~~~~~

-  ``commands``: A list of lists containing strings. Each top-level item
   is a single command, while the strings inside each list comprise
   parts of a command. This allows for proper shell argument escaping.
   To circumvent escaping, simply put the entire command in a single
   string, the command will additionally be evaluated in a shell
   (e.g. globbing will work).
   In addition to the manifest variables ``{root}`` is also available.
   It points at the root of the image volume.
   ``required``
   ``manifest vars``

Example
~~~~~~~

Create an empty `index.html` in `/var/www` and delete all locales except english.

.. code-block:: yaml

  commands:
    commands:
      - [touch, '{root}/var/www/index.html']
      - ['rm -rf /usr/share/locale/[^en]*']
