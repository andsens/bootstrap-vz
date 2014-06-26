
How bootstrap-vz works
======================

Tasks
~~~~~
At its core bootstrap-vz is based on tasks that perform units of work.
By keeping those tasks small and with a solid structure built around
them a high degree of flexibility can be achieved. To ensure that
tasks are executed in the right order, each task is placed in a
dependency graph where directed edges dictate precedence. Each task is
a simple class that defines its predecessor tasks and successor tasks
via attributes. Here is an example:

::

    class MapPartitions(Task):
    	description = 'Mapping volume partitions'
    	phase = phases.volume_preparation
    	predecessors = [PartitionVolume]
    	successors = [filesystem.Format]
    
    	@classmethod
    	def run(cls, info):
    		info.volume.partition_map.map(info.volume)

In this case the attributes define that the task at hand should run
after the ``PartitionVolume`` task — i.e. after volume has been
partitioned (``predecessors``) — but before formatting each
partition (``successors``).
It is also placed in the ``volume_preparation`` phase.
Phases are ordered and group tasks together. All tasks in a phase are
run before proceeding with the tasks in the next phase. They are a way
of avoiding the need to list 50 different tasks as predecessors and
successors.

The final task list that will be executed is computed by enumerating
all tasks in the package, placing them in the graph and
`sorting them topologically <http://en.wikipedia.org/wiki/Topological_sort>`_.
Subsequently the list returned is filtered to contain only the tasks the
provider and the plugins added to the taskset.


System abstractions
~~~~~~~~~~~~~~~~~~~
There are several abstractions in bootstrap-vz that make it possible
to generalize things like volume creation, partitioning, mounting and
package installation. As a rule these abstractions are located in the
``base/`` folder, where the manifest parsing and task ordering algorithm
are placed as well.
