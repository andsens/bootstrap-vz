from base import Task
from common import phases
import volume


class Create(Task):
	description = 'Creating a loopback volume'
	phase = phases.volume_creation
	before = [volume.Attach]

	def run(self, info):
		loopback_filename = 'loopback-{id:x}.img'.format(id=info.run_id)
		import os.path
		image_path = os.path.join(info.manifest.volume['loopback_dir'], loopback_filename)
		info.volume.create(image_path)
