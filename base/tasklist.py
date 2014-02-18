from common.exceptions import TaskListError
import logging
log = logging.getLogger(__name__)


class TaskList(object):

	def __init__(self):
		self.tasks = set()
		self.tasks_completed = []

	def load(self, function, manifest, *args):
		getattr(manifest.modules['provider'], function)(self.tasks, manifest, *args)
		for plugin in manifest.modules['plugins']:
			fn = getattr(plugin, function, None)
			if callable(fn):
				fn(self.tasks, manifest, *args)

	def run(self, info={}, dry_run=False):
		task_list = self.create_list()
		log.debug('Tasklist:\n\t{list}'.format(list='\n\t'.join(map(repr, task_list))))

		for task in task_list:
			if hasattr(task, 'description'):
				log.info(task.description)
			else:
				log.info('Running {task}'.format(task=task))
			if not dry_run:
				task.run(info)
			self.tasks_completed.append(task)

	def create_list(self):
		from common.phases import order
		# Get a hold of all tasks
		tasks = self.get_all_tasks()
		# Make sure the taskset is a subset of all the tasks we have gathered
		self.tasks.issubset(tasks)
		# Create a graph over all tasks by creating a map of each tasks successors
		graph = {}
		for task in tasks:
			# Do a sanity check first
			self.check_ordering(task)
			successors = set()
			# Add all successors mentioned in the task
			successors.update(task.successors)
			# Add all tasks that mention this task as a predecessor
			successors.update(filter(lambda succ: task in succ.predecessors, tasks))
			# Create a list of phases that succeed the phase of this task
			succeeding_phases = order[order.index(task.phase) + 1:]
			# Add all tasks that occur in above mentioned succeeding phases
			successors.update(filter(lambda succ: succ.phase in succeeding_phases, tasks))
			# Map the successors to the task
			graph[task] = successors

		components = self.strongly_connected_components(graph)
		cycles_found = 0
		for component in components:
			if len(component) > 1:
				cycles_found += 1
				log.debug('Cycle: {list}\n'.format(list=', '.join(map(repr, component))))
		if cycles_found > 0:
			msg = ('{0} cycles were found in the tasklist, '
			       'consult the logfile for more information.'.format(cycles_found))
			raise TaskListError(msg)

		# Run a topological sort on the graph, returning an ordered list
		sorted_tasks = self.topological_sort(graph)

		# Filter out any tasks not in the tasklist
		# We want to maintain ordering, so we don't use set intersection
		sorted_tasks = filter(lambda task: task in self.tasks, sorted_tasks)
		return sorted_tasks

	def get_all_tasks(self):
		# Get a generator that returns all classes in the package
		classes = self.get_all_classes('..')

		# lambda function to check whether a class is a task (excluding the superclass Task)
		def is_task(obj):
			from task import Task
			return issubclass(obj, Task) and obj is not Task
		return filter(is_task, classes)  # Only return classes that are tasks

	# Given a path, retrieve all the classes in it
	def get_all_classes(self, path=None):
		import pkgutil
		import importlib
		import inspect

		def walk_error(module):
			raise Exception('Unable to inspect module `{module}\''.format(module=module))
		walker = pkgutil.walk_packages(path, '', walk_error)
		for _, module_name, _ in walker:
			module = importlib.import_module(module_name)
			classes = inspect.getmembers(module, inspect.isclass)
			for class_name, obj in classes:
				# We only want classes that are defined in the module, and not imported ones
				if obj.__module__ == module_name:
						yield obj

	def check_ordering(self, task):
		for successor in task.successors:
			if successor.phase > successor.phase:
				msg = ("The task {task} is specified as running before {other}, "
				       "but its phase '{phase}' lies after the phase '{other_phase}'"
				       .format(task=task, other=successor, phase=task.phase, other_phase=successor.phase))
				raise TaskListError(msg)
		for predecessor in task.predecessors:
			if task.phase < predecessor.phase:
				msg = ("The task {task} is specified as running after {other}, "
				       "but its phase '{phase}' lies before the phase '{other_phase}'"
				       .format(task=task, other=predecessor, phase=task.phase, other_phase=predecessor.phase))
				raise TaskListError(msg)

	def strongly_connected_components(self, graph):
		# Source: http://www.logarithmic.net/pfh-files/blog/01208083168/sort.py
		# Find the strongly connected components in a graph using Tarjan's algorithm.
		# graph should be a dictionary mapping node names to lists of successor nodes.

		result = []
		stack = []
		low = {}

		def visit(node):
			if node in low:
				return

			num = len(low)
			low[node] = num
			stack_pos = len(stack)
			stack.append(node)

			for successor in graph[node]:
				visit(successor)
				low[node] = min(low[node], low[successor])

			if num == low[node]:
				component = tuple(stack[stack_pos:])
				del stack[stack_pos:]
				result.append(component)
				for item in component:
					low[item] = len(graph)

		for node in graph:
			visit(node)

		return result

	def topological_sort(self, graph):
		# Source: http://www.logarithmic.net/pfh-files/blog/01208083168/sort.py
		count = {}
		for node in graph:
			count[node] = 0
		for node in graph:
			for successor in graph[node]:
				count[successor] += 1

		ready = [node for node in graph if count[node] == 0]

		result = []
		while ready:
			node = ready.pop(-1)
			result.append(node)

			for successor in graph[node]:
				count[successor] -= 1
				if count[successor] == 0:
					ready.append(successor)

		return result
