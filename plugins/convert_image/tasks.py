from base import Task
from common import phases
from common.tasks.filesystem import DeleteMountDir


class ConvertImage(Task):
	description = 'Convert raw image'
	phase = phases.image_conversion

	def run(self, info):
		from common.tools import log_check_call
		converted_file = info.loopback_file.replace('img',info.manifest.plugins['convert_image']['format'])
		log_check_call(['/usr/bin/qemu-img', 'convert', '-O', info.manifest.plugins['convert_image']['format'], info.loopback_file, converted_file])
		import os
		os.remove(info.loopback_file)
		
