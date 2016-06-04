from abstract import AbstractPartition
import os.path
from bootstrapvz.common.tools import log_check_call


class Mount(object):
    """Represents a mount into the partition
    """
    def __init__(self, source, destination, opts):
        """
        :param str,AbstractPartition source: The path from where we mount or a partition
        :param str destination: The path of the mountpoint
        :param list opts: List of options to pass to the mount command
        """
        self.source      = source
        self.destination = destination
        self.opts        = opts

    def mount(self, prefix):
        """Performs the mount operation or forwards it to another partition

        :param str prefix: Path prefix of the mountpoint
        """
        mount_dir = os.path.join(prefix, self.destination)
        # If the source is another partition, we tell that partition to mount itself
        if isinstance(self.source, AbstractPartition):
            self.source.mount(destination=mount_dir)
        else:
            log_check_call(['mount'] + self.opts + [self.source, mount_dir])
        self.mount_dir = mount_dir

    def unmount(self):
        """Performs the unmount operation or asks the partition to unmount itself
        """
        # If its a partition, it can unmount itself
        if isinstance(self.source, AbstractPartition):
            self.source.unmount()
        else:
            log_check_call(['umount', self.mount_dir])
        del self.mount_dir

    def __getstate__(self):
        state = self.__dict__.copy()
        state['__class__'] = self.__module__ + '.' + self.__class__.__name__
        return state

    def __setstate__(self, state):
        for key in state:
            self.__dict__[key] = state[key]
