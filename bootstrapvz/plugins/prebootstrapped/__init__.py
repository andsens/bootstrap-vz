import tasks
from bootstrapvz.providers.ec2.tasks import ebs
from bootstrapvz.plugins.minimize_size.tasks import dpkg
from bootstrapvz.providers.virtualbox.tasks import guest_additions
from bootstrapvz.common.tasks import loopback
from bootstrapvz.common.tasks import volume
from bootstrapvz.common.tasks import folder
from bootstrapvz.common.tasks import locale
from bootstrapvz.common.tasks import apt
from bootstrapvz.common.tasks import bootstrap
from bootstrapvz.common.tasks import filesystem
from bootstrapvz.common.tasks import partitioning


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    settings = manifest.plugins['prebootstrapped']
    skip_tasks = [ebs.Create,
                  loopback.Create,
                  folder.Create,

                  filesystem.Format,
                  partitioning.PartitionVolume,
                  filesystem.TuneVolumeFS,
                  filesystem.AddXFSProgs,
                  filesystem.CreateBootMountDir,

                  apt.DisableDaemonAutostart,
                  dpkg.InitializeBootstrapFilterList,
                  dpkg.CreateDpkgCfg,
                  dpkg.CreateBootstrapFilterScripts,
                  dpkg.FilterLocales,
                  dpkg.ExcludeDocs,
                  dpkg.DeleteBootstrapFilterScripts,
                  locale.GenerateLocale,
                  bootstrap.MakeTarball,
                  bootstrap.Bootstrap,
                  guest_additions.InstallGuestAdditions,
                  ]
    if manifest.volume['backing'] == 'ebs':
        if settings.get('snapshot', None) is not None:
            taskset.add(tasks.CreateFromSnapshot)
            [taskset.discard(task) for task in skip_tasks]
        else:
            taskset.add(tasks.Snapshot)
    elif manifest.volume['backing'] == 'folder':
        if settings.get('folder', None) is not None:
            taskset.add(tasks.CreateFromFolder)
            [taskset.discard(task) for task in skip_tasks]
        else:
            taskset.add(tasks.CopyFolder)
    else:
        if settings.get('image', None) is not None:
            taskset.add(tasks.CreateFromImage)
            [taskset.discard(task) for task in skip_tasks]
        else:
            taskset.add(tasks.CopyImage)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    if manifest.volume['backing'] == 'ebs':
        counter_task(taskset, tasks.CreateFromSnapshot, volume.Delete)
    elif manifest.volume['backing'] == 'folder':
        counter_task(taskset, tasks.CreateFromFolder, folder.Delete)
    else:
        counter_task(taskset, tasks.CreateFromImage, volume.Delete)
