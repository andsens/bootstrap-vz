from base import Task
from common import phases
from common.tasks import loopback


class ConvertImage(Task):
	description = 'Converting raw image'
	phase = phases.image_registration
	before = [loopback.MoveImage]

	def run(self, info):
		from common.tools import log_check_call
		converted_file = info.loopback_file.replace('img', info.manifest.plugins['convert_image']['format'])
		log_check_call(['/usr/bin/qemu-img', 'convert', '-O', info.manifest.plugins['convert_image']['format'], info.loopback_file, converted_file])
		import os
		os.remove(info.loopback_file)
