import bootstrapvz.common.tasks.apt
import bootstrapvz.common.tasks.boot
import bootstrapvz.common.tasks.image
from bootstrapvz.common.tasks import loopback, initd, ssh, volume, grub
from bootstrapvz.common import task_groups
from .tasks import apt, boot, configuration, image, packages


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    taskset.update(task_groups.get_standard_groups(manifest))
    taskset.update([bootstrapvz.common.tasks.apt.AddBackports,
                    bootstrapvz.common.tasks.apt.AddDefaultSources,
                    loopback.AddRequiredCommands,
                    loopback.Create,
                    packages.DefaultPackages,
                    configuration.GatherReleaseInformation,
                    boot.ConfigureGrub,
                    initd.InstallInitScripts,
                    bootstrapvz.common.tasks.boot.BlackListModules,
                    bootstrapvz.common.tasks.boot.UpdateInitramfs,
                    ssh.AddSSHKeyGeneration,
                    ssh.DisableSSHPasswordAuthentication,
                    ssh.DisableRootLogin,
                    apt.AddBaselineAptCache,
                    bootstrapvz.common.tasks.image.MoveImage,
                    image.CreateTarball,
                    volume.Delete,
                    ])
    taskset.discard(grub.SetGrubConsolOutputDeviceToSerial)

    if 'gcs_destination' in manifest.provider:
        taskset.add(image.UploadImage)
        if 'gce_project' in manifest.provider:
            taskset.add(image.RegisterImage)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    taskset.update(task_groups.get_standard_rollback_tasks(completed))
