from bootstrapvz.common import task_groups
from bootstrapvz.common.tasks import apt, dpkg, folder, filesystem
from bootstrapvz.common.tools import rel_path
from . import tasks.commands
from . import tasks.image
from . import tasks.settings


def validate_manifest(data, validator, error):
    schema_path = rel_path(__file__, 'manifest-schema.yml')
    validator(data, schema_path)


def resolve_tasks(taskset, manifest):
    taskset.update(task_groups.get_base_group(manifest))
    taskset.update([dpkg.CreateDpkgCfg,
                    folder.Create,
                    filesystem.CopyMountTable,
                    filesystem.RemoveMountTable,
                    folder.Delete,
                    ])
    taskset.update(task_groups.get_network_group(manifest))
    taskset.update(task_groups.get_apt_group(manifest))
    taskset.update(task_groups.get_locale_group(manifest))
    taskset.update(task_groups.security_group)
    taskset.update(task_groups.get_cleanup_group(manifest))

    # Let the autostart of daemons by apt remain disabled
    taskset.discard(apt.EnableDaemonAutostart)

    taskset.update([tasks.commands.AddRequiredCommands,
                    tasks.image.CreateDockerfileEntry,
                    tasks.image.CreateImage,
                    tasks.settings.DpkgUnsafeIo,
                    tasks.settings.AutoRemoveKernel,
                    tasks.settings.SystemdContainer
                    ])
    if 'labels' in manifest.provider:
        taskset.add(tasks.image.PopulateLabels)
    if 'dockerfile' in manifest.provider:
        taskset.add(tasks.image.AppendManifestDockerfile)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    taskset.update(task_groups.get_standard_rollback_tasks(completed))
