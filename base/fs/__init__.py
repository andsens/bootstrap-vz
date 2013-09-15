

def load_volume(data):
	from common.fs.loopbackvolume import LoopbackVolume
	from providers.ec2.volume import EBSVolume
	from providers.virtualbox.volume import VirtualBoxVolume
	from partitionmap import PartitionMap
	from nopartitions import NoPartitions
	partition_maps = {'none': NoPartitions,
	                  'gpt': PartitionMap,
	                  }
	partition_map = partition_maps.get(data['partitions']['type'])(data['partitions'])
	volume_backings = {'raw': LoopbackVolume,
	                   'vdi': VirtualBoxVolume,
	                   'ebs': EBSVolume
	                   }
	return volume_backings.get(data['backing'])(partition_map)
