from bootstrapvz.common import task_groups
from bootstrapvz.common.tasks import image
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import ssh
from bootstrapvz.common.tasks import volume
import tasks.api
import tasks.image
import tasks.network
import tasks.packages


def validate_manifest(data, validator, error):
	import os.path
	validator(data, os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))

	keys = ['username', 'password', 'identity-domain']
	if 'credentials' in data['provider']:
		if not all(key in data['provider']['credentials'] for key in keys):
			msg = 'All Oracle Compute Cloud credentials should be specified in the manifest'
			error(msg, ['provider', 'credentials'])
		if not data['provider'].get('container'):
			msg = 'The container to which the image will be uploaded should be specified'
			error(msg, ['provider'])


def resolve_tasks(taskset, manifest):
	taskset.update(task_groups.get_standard_groups(manifest))
	taskset.update(task_groups.ssh_group)

	taskset.update([loopback.AddRequiredCommands,
	                loopback.Create,
	                image.MoveImage,
	                ssh.DisableRootLogin,
	                volume.Delete,
	                tasks.image.CreateImageTarball,
	                tasks.network.InstallDHCPCD,
	                tasks.packages.DefaultPackages,
	                ])

	if 'credentials' in manifest.provider:
		taskset.add(tasks.api.Connect)
		taskset.add(tasks.image.UploadImageTarball)
		if manifest.provider.get('verify', False):
			taskset.add(tasks.image.DownloadImageTarball)
			taskset.add(tasks.image.CompareImageTarballs)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
	taskset.update(task_groups.get_standard_rollback_tasks(completed))
