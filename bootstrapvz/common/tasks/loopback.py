from bootstrapvz.base import Task
from .. import phases
import host
import volume


class AddRequiredCommands(Task):
	description = 'Adding commands required for creating loopback volumes'
	phase = phases.preparation
	successors = [host.CheckExternalCommands]

	@classmethod
	def run(cls, info):
		from ..fs.loopbackvolume import LoopbackVolume
		if isinstance(info.volume, LoopbackVolume):
			info.host_dependencies['qemu-img'] = 'qemu-utils'
			info.host_dependencies['losetup'] = 'mount'
		from ..fs.qemuvolume import QEMUVolume
		if isinstance(info.volume, QEMUVolume):
			info.host_dependencies['losetup'] = 'mount'


class Create(Task):
	description = 'Creating a loopback volume'
	phase = phases.volume_creation
	successors = [volume.Attach]

	@classmethod
	def run(cls, info):
		import os.path
		image_path = os.path.join(info.workspace, 'volume.' + info.volume.extension)
		info.volume.create(image_path)


class MoveImage(Task):
	description = 'Moving volume image'
	phase = phases.image_registration

	@classmethod
	def run(cls, info):
		image_name = info.manifest.image['name'].format(**info.manifest_vars)
		filename = image_name + '.' + info.volume.extension

		import os.path
		destination = os.path.join(info.manifest.bootstrapper['workspace'], filename)
		import shutil
		shutil.move(info.volume.image_path, destination)
		info.volume.image_path = destination
		import logging
		log = logging.getLogger(__name__)
		log.info('The volume image has been moved to ' + destination)
