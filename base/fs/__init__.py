

def load_volume(data, bootloader):
	from common.fs.loopbackvolume import LoopbackVolume
	from providers.ec2.ebsvolume import EBSVolume
	from common.fs.virtualdiskimage import VirtualDiskImage
	from common.fs.virtualmachinedisk import VirtualMachineDisk
	from partitionmaps.gpt import GPTPartitionMap
	from partitionmaps.msdos import MSDOSPartitionMap
	from partitionmaps.none import NoPartitions
	partition_maps = {'none': NoPartitions,
	                  'gpt': GPTPartitionMap,
	                  'msdos': MSDOSPartitionMap,
	                  }
	partition_map = partition_maps.get(data['partitions']['type'])(data['partitions'], bootloader)
	volume_backings = {'raw': LoopbackVolume,
	                   's3':  LoopbackVolume,
	                   'vdi': VirtualDiskImage,
	                   'vmdk': VirtualMachineDisk,
	                   'ebs': EBSVolume
	                   }
	return volume_backings.get(data['backing'])(partition_map)
