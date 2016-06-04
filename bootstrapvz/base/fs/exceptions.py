

class VolumeError(Exception):
    """Raised when an error occurs while interacting with the volume
    """
    pass


class PartitionError(Exception):
    """Raised when an error occurs while interacting with the partitions on the volume
    """
    pass
