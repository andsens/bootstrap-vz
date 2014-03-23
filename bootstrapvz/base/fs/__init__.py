

def load_volume(data, bootloader):
	"""Instantiates a volume that corresponds to the data in the manifest
	Args:
		data (dict): The 'volume' section from the manifest
		bootloader (str): Name of the bootloader the system will boot with

	Returns:
		Volume. The volume that represents all information pertaining to the volume we bootstrap on
	"""
	from bootstrapvz.common.fs.loopbackvolume import LoopbackVolume
	from bootstrapvz.providers.ec2.ebsvolume import EBSVolume
	from bootstrapvz.common.fs.virtualdiskimage import VirtualDiskImage
	from bootstrapvz.common.fs.virtualmachinedisk import VirtualMachineDisk
	# Create a mapping between valid partition maps in the manifest and their corresponding classes
	from partitionmaps.gpt import GPTPartitionMap
	from partitionmaps.msdos import MSDOSPartitionMap
	from partitionmaps.none import NoPartitions
	partition_maps = {'none': NoPartitions,
	                  'gpt': GPTPartitionMap,
	                  'msdos': MSDOSPartitionMap,
	                  }
	# Instantiate the partition map
	partition_map = partition_maps.get(data['partitions']['type'])(data['partitions'], bootloader)
	# Create a mapping between valid volume backings in the manifest and their corresponding classes
	volume_backings = {'raw': LoopbackVolume,
	                   's3':  LoopbackVolume,
	                   'vdi': VirtualDiskImage,
	                   'vmdk': VirtualMachineDisk,
	                   'ebs': EBSVolume
	                   }
	 # Create the volume with the partition map as an argument
	return volume_backings.get(data['backing'])(partition_map)
