from abstract import AbstractPartition


class SinglePartition(AbstractPartition):

	def _before_create(self, e):
		self.device_path = e.volume.device_path
