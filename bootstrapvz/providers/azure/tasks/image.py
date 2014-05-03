from bootstrapvz.base import Task
from bootstrapvz.common import phases


class ConvertToVhd(Task):
	description = 'Convert raw image to vhd disk'
	phase = phases.image_registration

	@classmethod
	def run(cls, info):
		image_name = info.manifest.image['name'].format(**info.manifest_vars)
		filename = image_name + '.vhd'
		import os.path
		destination = os.path.join(info.manifest.bootstrapper['workspace'], filename)

		file_size = os.path.getsize(info.volume.image_path)
		rounded_vol_size = str(((file_size / (1024 * 1024) + 1) * (1024 * 1024)))

		from bootstrapvz.common.tools import log_check_call
		log_check_call(['qemu-img', 'resize', info.volume.image_path, rounded_vol_size])
		log_check_call(['qemu-img', 'convert',
		                '-o', 'subformat=fixed',
		                '-O', 'vpc',
		                info.volume.image_path, destination])
		os.remove(info.volume.image_path)
		import logging
		log = logging.getLogger(__name__)
		log.info('The volume image has been moved to ' + destination)
