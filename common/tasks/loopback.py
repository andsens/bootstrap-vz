from base import Task
from common import phases
from filesystem import UnmountVolume
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
		                'bs=1M', 'seek='+str(info.manifest.volume['size']), 'count=0'])


class CreateQemuImg(Task):
	description = 'Creating a loopback volume with qemu'
	phase = phases.volume_creation

	def run(self, info):
		loopback_filename = 'loopback-{id:x}.img'.format(id=info.run_id)
		import os.path
		info.loopback_file = os.path.join(info.manifest.volume['loopback_dir'], loopback_filename)
		log_check_call(['/usr/bin/qemu-img', 'create', '-f', 'raw',
		                info.loopback_file, str(info.manifest.volume['size'])+'M'])


class Attach(Task):
	description = 'Attaching the loopback volume'
	phase = phases.volume_creation
	after = [Create, CreateQemuImg]

	def run(self, info):
		info.bootstrap_device = {}
		command = ['/sbin/losetup', '--show', '--find', info.loopback_file]
		[info.bootstrap_device['path']] = log_check_call(command)


class Detach(Task):
	description = 'Detaching the loopback volume'
	phase = phases.volume_unmounting
	after = [UnmountVolume]

	def run(self, info):
		log_check_call(['/sbin/losetup', '-d', info.bootstrap_device['path']])
		del info.bootstrap_device


class Delete(Task):
	description = 'Deleting the loopback volume'
	phase = phases.cleaning

	def run(self, info):
		from os import remove
		remove(info.loopback_file)
		del info.loopback_file
