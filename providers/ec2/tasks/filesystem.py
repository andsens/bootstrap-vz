from base import Task
from common import phases
from common.exceptions import TaskError


class FormatVolume(Task):
	description = 'Formatting the volume'
	phase = phases.volume_preparation
	after = []

	def run(self, info):
		import subprocess
		from os import devnull
		dev_path = info.bootstrap_device['path']
		mkfs = '/sbin/mkfs.{fs}'.format(fs=info.manifest.volume['filesystem'])
		try:
			with open(devnull, 'w') as dev_null:
				subprocess.check_call([mkfs, dev_path], stdout=dev_null, stderr=dev_null)
		except subprocess.CalledProcessError:
			raise TaskError('Unable to format the bootstrap device')


class TuneVolumeFS(Task):
	description = 'Tuning the bootstrap volume filesystem'
	phase = phases.volume_preparation
	after = [FormatVolume]

	def run(self, info):
		import subprocess
		from os import devnull
		dev_path = info.bootstrap_device['path']
		try:
			with open(devnull, 'w') as dev_null:
				subprocess.check_call(['/sbin/tune2fs', '-i', '0', dev_path], stdout=dev_null, stderr=dev_null)
		except subprocess.CalledProcessError:
			raise TaskError('Unable to disable the time based check interval for the bootstrap volume')


class AddXFSProgs(Task):
	description = 'Adding `xfsprogs\' to the image packages'
	phase = phases.preparation
	after = []

	def run(self, info):
		include, exclude = info.img_packages
		include.add('xfsprogs')
