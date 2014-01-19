from abstract import AbstractPartition


class SinglePartition(AbstractPartition):

	def get_start(self):
		from common.bytes import Bytes
		return Bytes(0)
