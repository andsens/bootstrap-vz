from base import Task
from common import phases
from common.tools import log_check_call


class Create(Task):
	description = 'Creating a loopback volume'
	phase = phases.volume_creation

	def run(self, info):
		loopback_filename = 'loopback-{id:x}.img'.format(id=info.run_id)
		import os.path
		info.loopback_file = os.path.join(info.manifest.volume['loopback_dir'], loopback_filename)
		log_check_call(['/bin/dd',
		                'if=/dev/zero', 'of='+info.loopback_file,
		                'bs=1M', 'seek='+info.manifest.volume['size'], 'count=0'])


class Attach(Task):
	description = 'Attaching the loopback volume'
	phase = phases.volume_creation
	after = [Create]

	def run(self, info):
		info.bootstrap_device = {}
		info.bootstrap_device['path'] = log_check_call(['/sbin/losetup', '--find'])
		log_check_call(['/sbin/losetup', info.bootstrap_device['path'], info.loopback_file])


class Detach(Task):
	description = 'Detaching the loopback volume'
	phase = phases.volume_unmounting

	def run(self, info):
		log_check_call(['/sbin/losetup', '-d', info.bootstrap_device['path']])
		del info.bootstrap_device


class Delete(Task):
	description = 'Deleting the loopback volume'
	phase = phases.cleaning

	def run(self, info):
		from os import remove
		remove(info.bootstrap_device['path'])
		del info.loopback_file
