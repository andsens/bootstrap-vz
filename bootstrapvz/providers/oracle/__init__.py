import bootstrapvz.common.tasks.image
from bootstrapvz.common import task_groups
from bootstrapvz.common.tasks import loopback, ssh, volume
from .tasks import api, image, network, packages


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))

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
                    bootstrapvz.common.tasks.image.MoveImage,
                    ssh.DisableRootLogin,
                    volume.Delete,
                    image.CreateImageTarball,
                    network.InstallDHCPCD,
                    packages.DefaultPackages,
                    ])

    if 'credentials' in manifest.provider:
        taskset.add(api.Connect)
        taskset.add(image.UploadImageTarball)
        if manifest.provider.get('verify', False):
            taskset.add(image.DownloadImageTarball)
            taskset.add(image.CompareImageTarballs)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    taskset.update(task_groups.get_standard_rollback_tasks(completed))
