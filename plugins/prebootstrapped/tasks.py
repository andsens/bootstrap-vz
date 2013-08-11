from base import Task
from common import phases
from providers.ec2.tasks import ebs
from common.tasks import loopback
from common.tasks import bootstrap
import time
import logging
log = logging.getLogger(__name__)


class Snapshot(ebs.Snapshot):
	description = 'Creating a snapshot of the bootstrapped volume'
	phase = phases.os_installation
	after = [bootstrap.Bootstrap]

	def run(self, info):
		super(Snapshot, self).run(info)
		msg = 'A snapshot of the bootstrapped volume was created. ID: {id}'.format(id=info.snapshot.id)
		log.info(msg)


class CreateFromSnapshot(Task):
	description = 'Creating EBS volume from a snapshot'
	phase = phases.volume_creation
	before = [ebs.Attach]

	def run(self, info):
		volume_size = int(info.manifest.volume['size']/1024)
		snapshot = info.manifest.plugins['prebootstrapped']['snapshot']
		info.volume = info.connection.create_volume(volume_size,
		                                            info.host['availabilityZone'],
		                                            snapshot=snapshot)
		while info.volume.volume_state() != 'available':
			time.sleep(5)
			info.volume.update()


class CopyImage(Task):
	description = 'Creating a snapshot of the bootstrapped volume'
	phase = phases.os_installation
	after = [bootstrap.Bootstrap]

	def run(self, info):
		import os.path
		from shutil import copyfile
		loopback_backup_name = 'loopback-{id:x}.img.backup'.format(id=info.run_id)
		image_copy_path = os.path.join('/tmp', loopback_backup_name)
		copyfile(info.loopback_file, image_copy_path)
		msg = 'A copy of the bootstrapped volume was created. Path: {path}'.format(path=image_copy_path)
		log.info(msg)


class CreateFromImage(Task):
	description = 'Creating loopback image from a copy'
	phase = phases.volume_creation
	before = [loopback.Attach]

	def run(self, info):
		loopback_filename = 'loopback-{id:x}.img'.format(id=info.run_id)
		import os.path
		info.loopback_file = os.path.join(info.manifest.volume['loopback_dir'], loopback_filename)
		loopback_backup_path = info.manifest.plugins['prebootstrapped']['image']
		from shutil import copyfile
		copyfile(loopback_backup_path, info.loopback_file)
