from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import image
from bootstrapvz.common.tools import log_check_call


class CreateImage(Task):
	description = 'Creating docker image'
	phase = phases.image_registration
	predecessors = [image.MoveImage]

	@classmethod
	def run(cls, info):
		from pipes import quote
		tar_cmd = ['tar', '--create', '--numeric-owner',
		           '--directory', info.volume.path, '.']
		docker_cmd = ['docker', 'import', '-',
		              info.manifest.provider['repository'] + ':' + info.manifest.provider['tag']]
		cmd = ' '.join(map(quote, tar_cmd)) + ' | ' + ' '.join(map(quote, docker_cmd))
		[info._docker['container_id']] = log_check_call(cmd, shell=True)
