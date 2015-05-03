Developing plugins
==================

Developing a plugin for bootstrap-vz is a fairly straightforward process,
since there is very little code overhead.

The process is the same whether you create an `internal <#internal-plugins>`__
or an `external <#external-plugins>`__ plugin (though you need to add
some code for package management when creating an external plugin)

Start by creating an ``__init__.py`` in your plugin folder.
The only obligatory function you need to implement is ``resolve_tasks()``.
This function adds tasks to be run to the tasklist:

.. code:: python

	def resolve_tasks(taskset, manifest):
		taskset.add(tasks.DoSomething)

The manifest variable holds the manifest the user specified,
with it you can determine settings for your plugin and e.g.
check of which release of Debian bootstrap-vz will create an image.

A task is a class with a static ``run()`` function and some meta-information:

.. code:: python

	class DoSomething(Task):
		description = 'Doing something'
		phase = phases.volume_preparation
		predecessors = [PartitionVolume]
		successors = [filesystem.Format]

		@classmethod
		def run(cls, info):
			pass

To read more about tasks and their ordering, check out the section on
`how bootstrap-vz works <index.html#tasks>`__.


Besides the ``resolve_tasks()`` function, there is also the ``resolve_rollback_tasks()``
function, which comes into play when something has gone awry while bootstrapping.
It should be used to clean up anything that was created during the bootstrapping
process. If you created temporary files for example, you can add a task to the
rollback taskset that deletes those files, you might even already have it because
you run it after an image has been successfully bootstrapped:

.. code:: python

	def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
		counter_task(taskset, tasks.DoSomething, tasks.UndoSomething)

In  ``resolve_rollback_tasks()`` you have access to the taskset
(this time it contains tasks that will be run during rollback), the manifest, and
the tasks that have already been run before the bootstrapping aborted (``completed``).

The last parameter is the ``counter_task()`` function, with it you can specify that
a specific task (2nd param) has to be in the taskset (1st param) for the rollback
task (3rd param) to be added. This saves code and makes it more readable than
running through the completed tasklist and checking each completed task.

You can also specify a ``validate_manifest()`` function.
Typically it looks like this:

.. code:: python

	def validate_manifest(data, validator, error):
		import os.path
		schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
		validator(data, schema_path)

This code validates the manifest against a schema in your plugin folder.
The schema is a `JSON schema <http://json-schema.org/>`__, since bootstrap-vz
supports `yaml <http://yaml.org/>`__, you can avoid a lot of curly braces
quotes:

.. code:: yaml

  $schema: http://json-schema.org/draft-04/schema#
  title: Example plugin manifest
  type: object
  properties:
    plugins:
      type: object
      properties:
        example:
          type: object
          properties:
            message: {type: string}
          required: [message]
          additionalProperties: false

In the schema above we check that the ``example`` plugin has a single property
named ``message`` with a string value (setting ``additionalProperties`` to ``false``
makes sure that users don't misspell optional attributes).

Internal plugins
----------------
Internal plugins are part of the bootstrap-vz package and distributed with it.
If you have developed a plugin that you think should be part of the package
because a lot of people might use it you can send a pull request to get it
included (just remember to `read the guidelines <contributing.html>`__ first).

External plugins
-----------------
External plugins are packages distributed separately from bootstrap-vz.
Separate distribution makes sense when your plugin solves a narrow problem scope
specific to your use-case or when the plugin contains proprietary code that you
would not like to share.
They integrate with bootstrap-vz by exposing an entry-point through ``setup.py``:

.. code:: python

	setup(name='example-plugin',
	      version=0.9.5,
	      packages=find_packages(),
	      include_package_data=True,
	      entry_points={'bootstrapvz.plugins': ['plugin_name = package_name.module_name']},
	      install_requires=['bootstrap-vz >= 0.9.5'],
	      )

Beyond ``setup.py`` the package might need a ``MANIFEST.in`` so that assets
like ``manifest-schema.yml`` are included when the package is built:

.. code::

	include example/manifest-schema.yml
	include example/README.rst

To test your package from source you can run ``python setup.py develop``
to register the package so that bootstrap-vz can find the entry-point of your
plugin.

An example plugin is available at `<https://github.com/andsens/bootstrap-vz-example-plugin>`__,
you can use it as a starting point for your own plugin.

Installing external plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Some plugins may not find their way to the python package index
(especially if it's in a private repo). They can of course still be installed
using pip:

.. code:: sh

	pip install git+ssh://git@github.com/username/repo#egg=plugin_name
