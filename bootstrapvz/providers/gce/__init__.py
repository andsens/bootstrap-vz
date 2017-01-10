from bootstrapvz.common import task_groups
import tasks.apt
import tasks.boot
import tasks.configuration
import tasks.image
import tasks.initd
import tasks.host
import tasks.packages
from bootstrapvz.common.tasks import apt, boot, image, loopback, initd
from bootstrapvz.common.tasks import ssh, volume, grub


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    from bootstrapvz.common.releases import stretch
    taskset.update(task_groups.get_standard_groups(manifest))
    taskset.update([apt.AddBackports,
                    apt.AddDefaultSources,
                    loopback.AddRequiredCommands,
                    loopback.Create,
                    tasks.packages.DefaultPackages,
                    tasks.configuration.GatherReleaseInformation,
                    tasks.host.DisableIPv6,
                    tasks.boot.ConfigureGrub,
                    initd.InstallInitScripts,
                    initd.AddExpandRoot,
                    initd.AdjustExpandRootScript,
                    tasks.initd.AdjustExpandRootDev,
                    boot.BlackListModules,
                    boot.UpdateInitramfs,
                    ssh.AddSSHKeyGeneration,
                    ssh.DisableSSHPasswordAuthentication,
                    ssh.DisableRootLogin,
                    tasks.apt.AddBaselineAptCache,
                    image.MoveImage,
                    tasks.image.CreateTarball,
                    volume.Delete,
                    ])
    taskset.discard(grub.SetGrubConsolOutputDeviceToSerial)

    # Temporary fix for Stretch
    if manifest.release == stretch:
        taskset.discard(initd.InstallInitScripts)
        taskset.discard(initd.AddExpandRoot)
        taskset.discard(initd.AdjustExpandRootScript)
        taskset.discard(tasks.initd.AdjustExpandRootDev)

    if 'gcs_destination' in manifest.provider:
        taskset.add(tasks.image.UploadImage)
        if 'gce_project' in manifest.provider:
            taskset.add(tasks.image.RegisterImage)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    taskset.update(task_groups.get_standard_rollback_tasks(completed))
