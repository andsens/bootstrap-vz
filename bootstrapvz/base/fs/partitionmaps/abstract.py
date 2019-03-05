from abc import ABCMeta
from abc import abstractmethod
from bootstrapvz.common.tools import log_check_call
from bootstrapvz.common.fsm_proxy import FSMProxy
from ..exceptions import PartitionError


class AbstractPartitionMap(FSMProxy):
    """Abstract representation of a partiton map
    This class is a finite state machine and represents the state of the real partition map
    """

    __metaclass__ = ABCMeta

    # States the partition map can be in
    events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'unmapped'},
              {'name': 'map', 'src': 'unmapped', 'dst': 'mapped'},
              {'name': 'unmap', 'src': 'mapped', 'dst': 'unmapped'},
              ]

    def __init__(self, bootloader):
        """
        :param str bootloader: Name of the bootloader we will use for bootstrapping
        """
        # Create the configuration for the state machine
        cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': {}}
        super(AbstractPartitionMap, self).__init__(cfg)

    def is_blocking(self):
        """Returns whether the partition map is blocking volume detach operations

        :rtype: bool
        """
        return self.fsm.current == 'mapped'

    def get_total_size(self):
        """Returns the total size the partitions occupy

        :return: The size of all partitions
        :rtype: Sectors
        """
        # We just need the endpoint of the last partition
        return self.partitions[-1].get_end()

    def create(self, volume):
        """Creates the partition map

        :param Volume volume: The volume to create the partition map on
        """
        self.fsm.create(volume=volume)

    @abstractmethod
    def _before_create(self, event):
        pass

    def map(self, volume):
        """Maps the partition map to device nodes

        :param Volume volume: The volume the partition map resides on
        """
        self.fsm.map(volume=volume)

    def _before_map(self, event):
        """
        :raises PartitionError: In case a partition could not be mapped.
        """
        volume = event.volume
        try:
            # Ask kpartx how the partitions will be mapped before actually attaching them.
            mappings = log_check_call(['kpartx', '-l', volume.device_path])
            import re
            regexp = re.compile(r'^(?P<name>.+[^\d](?P<p_idx>\d+)) : '
                                r'(?P<start_blk>\d) (?P<num_blks>\d+) '
                                r'{device_path} (?P<blk_offset>\d+)$'
                                .format(device_path=volume.device_path))
            log_check_call(['kpartx', '-as', volume.device_path])

            import os.path
            # Run through the kpartx output and map the paths to the partitions
            for mapping in mappings:
                match = regexp.match(mapping)
                if match is None:
                    raise PartitionError('Unable to parse kpartx output: ' + mapping)
                partition_path = os.path.join('/dev/mapper', match.group('name'))
                p_idx = int(match.group('p_idx')) - 1
                self.partitions[p_idx].map(partition_path)

            # Check if any partition was not mapped
            for idx, partition in enumerate(self.partitions):
                if partition.fsm.current not in ['mapped', 'formatted']:
                    raise PartitionError('kpartx did not map partition #' + str(partition.get_index()))

        except PartitionError:
            # Revert any mapping and reraise the error
            for partition in self.partitions:
                if partition.fsm.can('unmap'):
                    partition.unmap()
            log_check_call(['kpartx', '-ds', volume.device_path])
            raise

    def unmap(self, volume):
        """Unmaps the partition

        :param Volume volume: The volume to unmap the partition map from
        """
        self.fsm.unmap(volume=volume)

    def _before_unmap(self, event):
        """
        :raises PartitionError: If the a partition cannot be unmapped
        """
        volume = event.volume
        # Run through all partitions before unmapping and make sure they can all be unmapped
        for partition in self.partitions:
            if partition.fsm.cannot('unmap'):
                msg = 'The partition {partition} prevents the unmap procedure'.format(partition=partition)
                raise PartitionError(msg)
        # Actually unmap the partitions
        log_check_call(['kpartx', '-ds', volume.device_path])
        # Call unmap on all partitions
        for partition in self.partitions:
            partition.unmap()
