from base import BasePartition


class UnformattedPartition(BasePartition):

	events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'unmapped'},
	          {'name': 'map', 'src': 'unmapped', 'dst': 'mapped'},
	          {'name': 'unmap', 'src': 'mapped', 'dst': 'unmapped'},
	          ]

	def __init__(self, size, previous):
		super(UnformattedPartition, self).__init__(size, None, previous)
