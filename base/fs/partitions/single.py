from abstract import AbstractPartition


class SinglePartition(AbstractPartition):

	initial_state = 'created'

	def _before_create(self, e):
		pass
