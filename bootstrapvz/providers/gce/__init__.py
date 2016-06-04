from bootstrapvz.common import task_groups
import tasks.boot
import tasks.configuration
import tasks.image
import tasks.initd
import tasks.host
import tasks.packages
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import boot
from bootstrapvz.common.tasks import image
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import initd
from bootstrapvz.common.tasks import ssh
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import grub


def validate_manifest(data, validator, error):
    import os.path
    schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
    validator(data, schema_path)


def resolve_tasks(taskset, manifest):
    taskset.update(task_groups.get_standard_groups(manifest))

    taskset.update([apt.AddBackports,
                    loopback.AddRequiredCommands,
                    loopback.Create,
                    tasks.packages.DefaultPackages,
                    tasks.configuration.GatherReleaseInformation,
                    tasks.host.DisableIPv6,
                    tasks.boot.ConfigureGrub,
                    initd.AddExpandRoot,
                    initd.AdjustExpandRootScript,
                    tasks.initd.AdjustExpandRootDev,
                    initd.InstallInitScripts,
                    boot.BlackListModules,
                    boot.UpdateInitramfs,
                    ssh.AddSSHKeyGeneration,
                    ssh.DisableSSHPasswordAuthentication,
                    ssh.DisableRootLogin,
                    image.MoveImage,
                    tasks.image.CreateTarball,
                    volume.Delete,
                    ])
    taskset.discard(grub.SetGrubConsolOutputDeviceToSerial)

    if 'gcs_destination' in manifest.provider:
        taskset.add(tasks.image.UploadImage)
        if 'gce_project' in manifest.provider:
            taskset.add(tasks.image.RegisterImage)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    taskset.update(task_groups.get_standard_rollback_tasks(completed))
