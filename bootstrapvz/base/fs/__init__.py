

def load_volume(data, bootloader):
    """Instantiates a volume that corresponds to the data in the manifest

    :param dict data: The 'volume' section from the manifest
    :param str bootloader: Name of the bootloader the system will boot with

    :return: The volume that represents all information pertaining to the volume we bootstrap on.
    :rtype: Volume
    """
    # Map valid partition maps in the manifest and their corresponding classes
    from partitionmaps.gpt import GPTPartitionMap
    from partitionmaps.msdos import MSDOSPartitionMap
    from partitionmaps.none import NoPartitions
    partition_map = {'none': NoPartitions,
                     'gpt': GPTPartitionMap,
                     'msdos': MSDOSPartitionMap,
                     }.get(data['partitions']['type'])

    # Map valid volume backings in the manifest and their corresponding classes
    from bootstrapvz.common.fs.loopbackvolume import LoopbackVolume
    from bootstrapvz.providers.ec2.ebsvolume import EBSVolume
    from bootstrapvz.common.fs.virtualdiskimage import VirtualDiskImage
    from bootstrapvz.common.fs.virtualharddisk import VirtualHardDisk
    from bootstrapvz.common.fs.virtualmachinedisk import VirtualMachineDisk
    from bootstrapvz.common.fs.folder import Folder
    volume_backing = {'raw': LoopbackVolume,
                      's3':  LoopbackVolume,
                      'vdi': VirtualDiskImage,
                      'vhd': VirtualHardDisk,
                      'vmdk': VirtualMachineDisk,
                      'ebs': EBSVolume,
                      'folder': Folder
                      }.get(data['backing'])

    # Instantiate the partition map
    from bootstrapvz.common.bytes import Bytes
    # Only operate with a physical sector size of 512 bytes for now,
    # not sure if we can change that for some of the virtual disks
    sector_size = Bytes('512B')
    partition_map = partition_map(data['partitions'], sector_size, bootloader)

    # Create the volume with the partition map as an argument
    return volume_backing(partition_map)
