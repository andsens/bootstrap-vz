from functools import total_ordering


@total_ordering
class Task(object):
	description = None
	
	phase = None
	before = []
	after = []

	def __init__(self):
		self._check_ordering()

	def run(self, info):
		pass

	def _after(self, other):
		return self.phase > other.phase or type(self) in other.before or type(other) in self.after

	def _before(self, other):
		return self.phase < other.phase or type(other) in self.before or type(self) in other.after

	def __lt__(self, other):
		return self._before(other) and not self._after(other)

	def __gt__(self, other):
		return not self._before(other) and self._after(other)

	def __eq__(self, other):
		return not self._before(other) and not self._after(other)

	def __ne__(self, other):
		return self._before(other) or self._after(other)

	def __str__(self):
		return '{module}.{task}'.format(module=self.__module__, task=self.__class__.__name__)

	def _check_ordering(self):
		for task in self.before:
			if self.phase > task.phase:
				msg = ("The task {self} is specified as running before {other}, "
				       "but its phase {phase} lies after the phase {other_phase}"
				       .format(self, other, self.phase, other.phase))
				raise TaskOrderError(msg)
		for task in self.after:
			if self.phase < task.phase:
				msg = ("The task {self} is specified as running after {other}, "
				       "but its phase {phase} lies before the phase {other_phase}"
				       .format(self=self, other=other, phase=self.phase, other_phase=other.phase))
				raise TaskOrderError(msg)
		conflict = next(iter(set(self.before) &  set(self.after)), None)
		if conflict is not None:
				msg = ("The task {self} is specified as running both before and after {conflict}"
				       .format(self=self, conflict=conflict))
				raise TaskOrderError(msg)
