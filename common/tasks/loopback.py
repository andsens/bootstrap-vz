from base import Task
from common import phases
import volume


class Create(Task):
	description = 'Creating a loopback volume'
	phase = phases.volume_creation
	successors = [volume.Attach]

	def run(self, info):
		import os.path
		image_path = os.path.join(info.workspace, 'volume.{ext}'.format(ext=info.volume.extension))
		info.volume.create(image_path)


class MoveImage(Task):
	description = 'Moving volume image'
	phase = phases.image_registration

	def run(self, info):
		manifest_vars = {'release':        info.manifest.system['release'],
		                 'architecture':   info.manifest.system['architecture']}
		from datetime import datetime
		now = datetime.now()
		time_vars = ['%a', '%A', '%b', '%B', '%c', '%d', '%f', '%H',
		             '%I', '%j', '%m', '%M', '%p', '%S', '%U', '%w',
		             '%W', '%x', '%X', '%y', '%Y', '%z', '%Z']
		for var in time_vars:
			manifest_vars[var] = now.strftime(var)

		image_name = info.manifest.image['name'].format(**manifest_vars)
		filename = '{image_name}.{ext}'.format(image_name=image_name, ext=info.volume.extension)

		import os.path
		destination = os.path.join(info.manifest.bootstrapper['workspace'], filename)
		import shutil
		shutil.move(info.volume.image_path, destination)
		import logging
		log = logging.getLogger(__name__)
		log.info('The volume image has been moved to {image_path}'.format(image_path=destination))
