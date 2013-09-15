from base import Task
from common import phases
import volume


class Create(Task):
	description = 'Creating a loopback volume'
	phase = phases.volume_creation
	before = [volume.Attach]

	def run(self, info):
		import os.path
		image_path = os.path.join(info.workspace, 'volume.{ext}'.format(ext=info.volume.extension))
		info.volume.create(image_path)


class MoveImage(Task):
	description = 'Moving volume image'
	phase = phases.image_registration

	def run(self, info):
		import os.path
		filename = 'loopback-{id:x}.{ext}'.format(id=info.run_id, ext=info.volume.extension)
		destination = os.path.join(info.bootstrapper['workspace'], filename)
		import shutil
		shutil.move(info.volume.image_path, destination)
		import logging
		log = logging.getLogger(__name__)
		log.info('The volume image has been moved to {image_path}'.format(image_path=destination))
