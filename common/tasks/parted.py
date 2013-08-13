from base import Task
from common import phases
from common.tools import log_check_call
import filesystem
import loopback


class PartitionVolume(Task):
	description = 'Partitioning the volume'
	phase = phases.volume_preparation

	def run(self, info):
		# parted
		log_check_call(['parted', '-a', 'optimal', '-s', info.bootstrap_device['path'],
		                '--', 'mklabel', 'msdos'])
		log_check_call(['parted', '-a', 'optimal', '-s', info.bootstrap_device['path'],
		                '--', 'mkpart', 'primary', 'ext4', '32k', '-1'])
		log_check_call(['parted', '-s', info.bootstrap_device['path'],
		                '--', 'set', '1', 'boot', 'on'])


class MapPartitions(Task):
	description = 'Mapping volume partitions'
	phase = phases.volume_preparation
	after = [PartitionVolume]

	def run(self, info):
		root_partition_path =  info.bootstrap_device['path'].replace('/dev', '/dev/mapper')+'p1'
                log_check_call(['kpartx', '-a', '-v', info.bootstrap_device['path']])
		info.bootstrap_device['partitions'] = {'root_path': root_partition_path}


class FormatPartitions(Task):
	description = 'Formatting the partitions'
	phase = phases.volume_preparation
	before = [filesystem.TuneVolumeFS]
	after = [MapPartitions]

	def run(self, info):
		log_check_call(['/sbin/mkfs.{fs}'.format(fs=info.manifest.volume['filesystem']),
		                '-m', '1', '-v', info.bootstrap_device['partitions']['root_path']])


class UnmapPartitions(Task):
	description = 'Removing volume partitions mapping'
	phase = phases.volume_unmounting
	before = [loopback.Detach]
	after = [filesystem.UnmountVolume]

	def run(self, info):
		log_check_call(['kpartx', '-d', info.bootstrap_device['path']])
		del info.bootstrap_device['partitions']['root_path']
