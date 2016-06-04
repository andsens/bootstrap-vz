from base import BasePartition


class UnformattedPartition(BasePartition):
    """Represents an unformatted partition
    It cannot be mounted
    """

    # The states for our state machine. It can only be mapped, not mounted.
    events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'unmapped'},
              {'name': 'map', 'src': 'unmapped', 'dst': 'mapped'},
              {'name': 'unmap', 'src': 'mapped', 'dst': 'unmapped'},
              ]

    def __init__(self, size, previous):
        """
        :param Bytes size: Size of the partition
        :param BasePartition previous: The partition that preceeds this one
        """
        super(UnformattedPartition, self).__init__(size, None, None, previous)
