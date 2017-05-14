from bootstrapvz.common import task_groups
import tasks.packages
from bootstrapvz.common.tasks import image, loopback, initd, ssh, logicalvolume


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    taskset.update(task_groups.get_standard_groups(manifest))

    taskset.update([tasks.packages.DefaultPackages,
                    initd.InstallInitScripts,
                    ssh.AddOpenSSHPackage,
                    ssh.ShredHostkeys,
                    ssh.AddSSHKeyGeneration,
                    ])
    if manifest.volume.get('logicalvolume', []):
        taskset.update([logicalvolume.AddRequiredCommands,
                        logicalvolume.Create,
                        ])
    else:
        taskset.update([loopback.AddRequiredCommands,
                        loopback.Create,
                        image.MoveImage,
                        ])

    if manifest.provider.get('virtio', []):
        from tasks import virtio
        taskset.update([virtio.VirtIO])


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    taskset.update(task_groups.get_standard_rollback_tasks(completed))
    counter_task(taskset, logicalvolume.Create, logicalvolume.Delete)
