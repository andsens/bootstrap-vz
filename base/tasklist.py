from common.exceptions import TaskListError
import logging
log = logging.getLogger(__name__)


class TaskList(object):

	def __init__(self):
		self.tasks = set()

	def add(self, *args):
		self.tasks.update(args)

	def remove(self, task):
		self.tasks.discard(self.get(task))

	def replace(self, task, replacement):
		self.remove(task)
		self.add(replacement)

	def get(self, ref):
		return next(task for task in self.tasks if type(task) is ref)

	def run(self, bootstrap_info):
		task_list = self.create_list()
		log.debug('Tasklist:\n\t{list}'.format(list='\n\t'.join(repr(task) for task in task_list)))
		for task in task_list:
			log.info(task)
			task.run(bootstrap_info)

	def create_list(self):
		from common.phases import order
		graph = {}
		for task in self.tasks:
			graph[task] = []
			graph[task].extend([self.get(succ) for succ in task.before])
			graph[task].extend([succ for succ in self.tasks if type(task) in succ.after])
			succeeding_phases = order[order.index(task.phase)+1:]
			graph[task].extend([succ for succ in self.tasks if succ.phase in succeeding_phases])


		components = self.strongly_connected_components(graph)
		cycles_found = 0
		for component in components:
			if len(component) > 1:
				cycles_found += 1
				log.debug('Cycle: {list}\n'.format(list=', '.join(repr(task) for task in component)))
		if cycles_found > 0:
			msg = ('{0} cycles were found in the tasklist, '
			       'consult the logfile for more information.'.format(cycles_found))
			raise TaskListError(msg)

		sorted_tasks = self.topological_sort(graph)

		return sorted_tasks

	def strongly_connected_components(self, graph):
		# Source: http://www.logarithmic.net/pfh-files/blog/01208083168/sort.py
		# Find the strongly connected components in a graph using Tarjan's algorithm.
		# graph should be a dictionary mapping node names to lists of successor nodes.

		result = [ ]
		stack = [ ]
		low = { }

		def visit(node):
			if node in low: return

			num = len(low)
			low[node] = num
			stack_pos = len(stack)
			stack.append(node)

			for successor in graph[node]:
				# print successor
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
		count = { }
		for node in graph:
			count[node] = 0
		for node in graph:
			for successor in graph[node]:
				count[successor] += 1

		ready = [ node for node in graph if count[node] == 0 ]

		result = [ ]
		while ready:
			node = ready.pop(-1)
			result.append(node)

			for successor in graph[node]:
				count[successor] -= 1
				if count[successor] == 0:
					ready.append(successor)

		return result
