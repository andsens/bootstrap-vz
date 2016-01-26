from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import image
from bootstrapvz.common.tools import log_check_call
import os


class CreateImageTarball(Task):
	description = 'Creating tarball with image'
	phase = phases.image_registration
	predecessors = [image.MoveImage]

	@classmethod
	def run(cls, info):
		image_name = info.manifest.name.format(**info.manifest_vars)
		filename = image_name + '.' + info.volume.extension

		tarball_name = image_name + '.tar.gz'
		tarball_path = os.path.join(info.manifest.bootstrapper['workspace'], tarball_name)
		log_check_call(['tar', '--sparse', '-C', info.manifest.bootstrapper['workspace'],
		                '-caf', tarball_path, filename])
