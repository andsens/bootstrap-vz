from base import Task
from common import phases
import volume


class Create(Task):
	description = 'Creating a loopback volume'
	phase = phases.volume_creation
	successors = [volume.Attach]

	@classmethod
	def run(cls, info):
		import os.path
		image_path = os.path.join(info.workspace, 'volume.{ext}'.format(ext=info.volume.extension))
		info.volume.create(image_path)


class MoveImage(Task):
	description = 'Moving volume image'
	phase = phases.image_registration

	@classmethod
	def run(cls, info):
		image_name = info.manifest.image['name'].format(**info.manifest_vars)
		filename = '{image_name}.{ext}'.format(image_name=image_name, ext=info.volume.extension)

		import os.path
		destination = os.path.join(info.manifest.bootstrapper['workspace'], filename)
		import shutil
		shutil.move(info.volume.image_path, destination)
		import logging
		log = logging.getLogger(__name__)
		log.info('The volume image has been moved to {image_path}'.format(image_path=destination))
