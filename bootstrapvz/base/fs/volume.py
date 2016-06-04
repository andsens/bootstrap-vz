from abc import ABCMeta
from bootstrapvz.common.fsm_proxy import FSMProxy
from bootstrapvz.common.tools import log_check_call
from .exceptions import VolumeError
from partitionmaps.none import NoPartitions


class Volume(FSMProxy):
    """Represents an abstract volume.
    This class is a finite state machine and represents the state of the real volume.
    """

    __metaclass__ = ABCMeta

    # States this volume can be in
    events = [{'name': 'create', 'src': 'nonexistent', 'dst': 'detached'},
              {'name': 'attach', 'src': 'detached', 'dst': 'attached'},
              {'name': 'link_dm_node', 'src': 'attached', 'dst': 'linked'},
              {'name': 'unlink_dm_node', 'src': 'linked', 'dst': 'attached'},
              {'name': 'detach', 'src': 'attached', 'dst': 'detached'},
              {'name': 'delete', 'src': 'detached', 'dst': 'deleted'},
              ]

    def __init__(self, partition_map):
        """
        :param PartitionMap partition_map: The partition map for the volume
        """
        # Path to the volume
        self.device_path = None
        # The partition map
        self.partition_map = partition_map
        # The size of the volume as reported by the partition map
        self.size = self.partition_map.get_total_size()

        # Before detaching, check that nothing would block the detachment
        callbacks = {'onbeforedetach': self._check_blocking}
        if isinstance(self.partition_map, NoPartitions):
            # When the volume has no partitions, the virtual root partition path is equal to that of the volume
            # Update that path whenever the path to the volume changes
            def set_dev_path(e):
                self.partition_map.root.device_path = self.device_path
            callbacks['onafterattach'] = set_dev_path
            callbacks['onafterdetach'] = set_dev_path  # Will become None
            callbacks['onlink_dm_node'] = set_dev_path
            callbacks['onunlink_dm_node'] = set_dev_path

        # Create the configuration for our finite state machine
        cfg = {'initial': 'nonexistent', 'events': self.events, 'callbacks': callbacks}
        super(Volume, self).__init__(cfg)

    def _after_create(self, e):
        if isinstance(self.partition_map, NoPartitions):
            # When the volume has no partitions, the virtual root partition
            # is essentially created when the volume is created, forward that creation event.
            self.partition_map.root.create()

    def _check_blocking(self, e):
        """Checks whether the volume is blocked

        :raises VolumeError: When the volume is blocked from being detached
        """
        # Only the partition map can block the volume
        if self.partition_map.is_blocking():
            raise VolumeError('The partitionmap prevents the detach procedure')

    def _before_link_dm_node(self, e):
        """Links the volume using the device mapper
        This allows us to create a 'window' into the volume that acts like a volume in itself.
        Mainly it is used to fool grub into thinking that it is working with a real volume,
        rather than a loopback device or a network block device.

        :param _e_obj e: Event object containing arguments to create()

        Keyword arguments to link_dm_node() are:

        :param int logical_start_sector: The sector the volume should start at in the new volume
        :param int start_sector: The offset at which the volume should begin to be mapped in the new volume
        :param int sectors: The number of sectors that should be mapped

        Read more at: http://manpages.debian.org/cgi-bin/man.cgi?query=dmsetup&apropos=0&sektion=0&manpath=Debian+7.0+wheezy&format=html&locale=en

        :raises VolumeError: When a free block device cannot be found.
        """
        import os.path
        from bootstrapvz.common.fs import get_partitions
        # Fetch information from /proc/partitions
        proc_partitions = get_partitions()
        device_name = os.path.basename(self.device_path)
        device_partition = proc_partitions[device_name]

        # The sector the volume should start at in the new volume
        logical_start_sector = getattr(e, 'logical_start_sector', 0)

        # The offset at which the volume should begin to be mapped in the new volume
        start_sector = getattr(e, 'start_sector', 0)

        # The number of sectors that should be mapped
        sectors = getattr(e, 'sectors', int(self.size) - start_sector)

        # This is the table we send to dmsetup, so that it may create a device mapping for us.
        table = ('{log_start_sec} {sectors} linear {major}:{minor} {start_sec}'
                 .format(log_start_sec=logical_start_sector,
                         sectors=sectors,
                         major=device_partition['major'],
                         minor=device_partition['minor'],
                         start_sec=start_sector))
        import string
        import os.path
        # Figure out the device letter and path
        for letter in string.ascii_lowercase:
            dev_name = 'vd' + letter
            dev_path = os.path.join('/dev/mapper', dev_name)
            if not os.path.exists(dev_path):
                self.dm_node_name = dev_name
                self.dm_node_path = dev_path
                break

        if not hasattr(self, 'dm_node_name'):
            raise VolumeError('Unable to find a free block device path for mounting the bootstrap volume')

        # Create the device mapping
        log_check_call(['dmsetup', 'create', self.dm_node_name], table)
        # Update the device_path but remember the old one for when we unlink the volume again
        self.unlinked_device_path = self.device_path
        self.device_path = self.dm_node_path

    def _before_unlink_dm_node(self, e):
        """Unlinks the device mapping
        """
        log_check_call(['dmsetup', 'remove', self.dm_node_name])
        # Reset the device_path
        self.device_path = self.unlinked_device_path
        # Delete the no longer valid information
        del self.unlinked_device_path
        del self.dm_node_name
        del self.dm_node_path
