from common.exceptions import TaskListError


class Task(object):
	description = None
	
	phase = None
	before = []
	after = []

	def __init__(self):
		self._check_ordering()

	def run(self, info):
		pass

	def __str__(self):
		return '{module}.{task}'.format(module=self.__module__, task=self.__class__.__name__)

	def __repr__(self):
		return self.__str__()

	def _check_ordering(self):
		def name(ref):
			return '{module}.{task}'.format(module=ref.__module__, task=ref.__class__.__name__)
		for task in self.before:
			if self.phase > task.phase:
				msg = ("The task {self} is specified as running before {other}, "
				       "but its phase {phase} lies after the phase {other_phase}"
				       .format(self=type(self), other=task, phase=self.phase, other_phase=task.phase))
				raise TaskListError(msg)
		for task in self.after:
			if self.phase < task.phase:
				msg = ("The task {self} is specified as running after {other}, "
				       "but its phase {phase} lies before the phase {other_phase}"
				       .format(self=type(self), other=task, phase=self.phase, other_phase=task.phase))
				raise TaskListError(msg)
