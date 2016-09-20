from bootstrapvz.common import task_groups
import tasks.packages
import tasks.boot
from bootstrapvz.common.tasks import image
from bootstrapvz.common.tasks import loopback


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    taskset.update(task_groups.get_standard_groups(manifest))

    taskset.update([tasks.packages.DefaultPackages,
                    tasks.boot.AddVirtualConsoleGrubOutputDevice,
                    loopback.AddRequiredCommands,
                    loopback.Create,
                    image.MoveImage,
                    ])

    if manifest.provider.get('guest_additions', False):
        from tasks import guest_additions
        taskset.update([guest_additions.CheckGuestAdditionsPath,
                        guest_additions.AddGuestAdditionsPackages,
                        guest_additions.InstallGuestAdditions,
                        ])


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    taskset.update(task_groups.get_standard_rollback_tasks(completed))
