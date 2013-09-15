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


class MoveImage(Task):
	description = 'Moving volume image'
	phase = phases.image_registration

	def run(self, info):
		import os.path
		image_basename = os.path.basename(info.volume.image_path)
		destination = os.path.join(info.manifest.bootstrapper['workspace'], image_basename)
		import shutil
		shutil.move(info.volume.image_path, destination)
		import logging
		log = logging.getLogger(__name__)
		log.info('The volume image has been moved to {image_path}'.format(image_path=destination))
