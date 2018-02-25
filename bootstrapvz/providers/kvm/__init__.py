from bootstrapvz.common import task_groups
from bootstrapvz.common.tasks import image, loopback, initd, ssh, logicalvolume
from .tasks import packages, boot


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    taskset.update(task_groups.get_standard_groups(manifest))

    taskset.update([packages.DefaultPackages,
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
        from .tasks import virtio
        taskset.update([virtio.VirtIO])

    if manifest.provider.get('console', False):
        if manifest.provider['console'] == 'virtual':
            taskset.update([boot.SetGrubConsolOutputDeviceToVirtual])

            from bootstrapvz.common.releases import jessie
            if manifest.release >= jessie:
                taskset.update([boot.SetGrubConsolOutputDeviceToVirtual,
                                boot.SetSystemdTTYVTDisallocate,
                                ])


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    taskset.update(task_groups.get_standard_rollback_tasks(completed))
    counter_task(taskset, logicalvolume.Create, logicalvolume.Delete)
