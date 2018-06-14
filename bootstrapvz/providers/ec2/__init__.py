from bootstrapvz.common import task_groups
from .tasks import packages, connection, host, ami, ebs, filesystem, boot, network, initd, tuning
import bootstrapvz.common.tasks.boot
import bootstrapvz.common.tasks.filesystem
import bootstrapvz.common.tasks.grub
import bootstrapvz.common.tasks.initd
from bootstrapvz.common.tasks import apt, kernel, loopback, volume
from bootstrapvz.common.tools import rel_path


def validate_manifest(data, validator, error):
    validator(data, rel_path(__file__, 'manifest-schema.yml'))

    from bootstrapvz.common.bytes import Bytes
    if data['volume']['backing'] == 'ebs':
        volume_size = Bytes(0)
        for key, partition in data['volume']['partitions'].iteritems():
            if key != 'type':
                volume_size += Bytes(partition['size'])
        if int(volume_size % Bytes('1GiB')) != 0:
            msg = ('The volume size must be a multiple of 1GiB when using EBS backing')
            error(msg, ['volume', 'partitions'])
    else:
        validator(data, rel_path(__file__, 'manifest-schema-s3.yml'))

    bootloader = data['system']['bootloader']
    virtualization = data['provider']['virtualization']
    encrypted = data['provider'].get('encrypted', False)
    kms_key_id = data['provider'].get('kms_key_id', None)
    backing = data['volume']['backing']
    partition_type = data['volume']['partitions']['type']
    enhanced_networking = data['provider']['enhanced_networking'] if 'enhanced_networking' in data['provider'] else None

    if virtualization == 'pvm' and bootloader != 'pvgrub':
        error('Paravirtualized AMIs only support pvgrub as a bootloader', ['system', 'bootloader'])

    if backing != 'ebs' and virtualization == 'hvm':
            error('HVM AMIs currently only work when they are EBS backed', ['volume', 'backing'])

    if backing == 's3' and partition_type != 'none':
            error('S3 backed AMIs currently only work with unpartitioned volumes', ['system', 'bootloader'])

    if backing != 'ebs' and encrypted:
            error('Encryption is supported only on EBS volumes')

    if encrypted is False and kms_key_id is not None:
            error('KMS Key Id can be set only when encryption is enabled')

    if enhanced_networking == 'simple' and virtualization != 'hvm':
            error('Enhanced networking only works with HVM virtualization', ['provider', 'virtualization'])


def resolve_tasks(taskset, manifest):
    """
    Function setting up tasks to run for this provider
    """
    from bootstrapvz.common.releases import wheezy, jessie, stable

    taskset.update(task_groups.get_standard_groups(manifest))
    taskset.update(task_groups.ssh_group)

    taskset.update([host.AddExternalCommands,
                    packages.DefaultPackages,
                    connection.SilenceBotoDebug,
                    connection.GetCredentials,
                    ami.AMIName,
                    connection.Connect,

                    tuning.TuneSystem,
                    tuning.BlackListModules,
                    bootstrapvz.common.tasks.boot.BlackListModules,
                    bootstrapvz.common.tasks.boot.DisableGetTTYs,
                    boot.AddXenGrubConsoleOutputDevice,
                    bootstrapvz.common.tasks.grub.WriteGrubConfig,
                    boot.UpdateGrubConfig,
                    bootstrapvz.common.tasks.initd.AddExpandRoot,
                    bootstrapvz.common.tasks.initd.RemoveHWClock,
                    bootstrapvz.common.tasks.initd.InstallInitScripts,
                    ami.RegisterAMI,
                    ])

    if manifest.release > wheezy:
        taskset.add(network.InstallNetworkingUDevHotplugAndDHCPSubinterface)

    if manifest.release <= wheezy:
        # The default DHCP client `isc-dhcp' doesn't work properly on wheezy and earlier
        taskset.add(network.InstallDHCPCD)
        taskset.add(network.EnableDHCPCDDNS)

    if manifest.release >= jessie:
        taskset.add(packages.AddWorkaroundGrowpart)
        taskset.add(bootstrapvz.common.tasks.initd.AdjustGrowpartWorkaround)
        if manifest.system['bootloader'] == 'grub':
            taskset.add(bootstrapvz.common.tasks.grub.EnableSystemd)
        if manifest.release <= stable:
            taskset.add(apt.AddBackports)

    if manifest.provider.get('install_init_scripts', True):
        taskset.add(initd.AddEC2InitScripts)

    if manifest.volume['partitions']['type'] != 'none':
        taskset.add(bootstrapvz.common.tasks.initd.AdjustExpandRootScript)

    if manifest.system['bootloader'] == 'pvgrub':
        taskset.add(bootstrapvz.common.tasks.grub.AddGrubPackage)
        taskset.update([bootstrapvz.common.tasks.grub.AddGrubPackage,
                        bootstrapvz.common.tasks.grub.InitGrubConfig,
                        bootstrapvz.common.tasks.grub.SetGrubTerminalToConsole,
                        bootstrapvz.common.tasks.grub.SetGrubConsolOutputDeviceToSerial,
                        bootstrapvz.common.tasks.grub.RemoveGrubTimeout,
                        bootstrapvz.common.tasks.grub.DisableGrubRecovery,
                        boot.CreatePVGrubCustomRule,
                        boot.ConfigurePVGrub,
                        bootstrapvz.common.tasks.grub.WriteGrubConfig,
                        boot.UpdateGrubConfig,
                        boot.LinkGrubConfig])

    if manifest.volume['backing'].lower() == 'ebs':
        taskset.update([host.GetInstanceMetadata,
                        ebs.Create,
                        ebs.Snapshot,
                        ])
        taskset.add(ebs.Attach)
        taskset.discard(volume.Attach)

    if manifest.volume['backing'].lower() == 's3':
        taskset.update([loopback.AddRequiredCommands,
                        host.SetRegion,
                        loopback.Create,
                        filesystem.S3FStab,
                        ami.BundleImage,
                        ami.UploadImage,
                        ami.RemoveBundle,
                        ])
        taskset.discard(bootstrapvz.common.tasks.filesystem.FStab)

    if manifest.provider.get('enhanced_networking', None) == 'simple':
        taskset.update([kernel.AddDKMSPackages,
                        network.InstallEnhancedNetworking,
                        network.InstallENANetworking,
                        kernel.UpdateInitramfs])

    taskset.update([bootstrapvz.common.tasks.filesystem.Format,
                    volume.Delete,
                    ])


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    taskset.update(task_groups.get_standard_rollback_tasks(completed))
    counter_task(taskset, ebs.Create, volume.Delete)
    counter_task(taskset, ebs.Attach, volume.Detach)
    counter_task(taskset, ami.BundleImage, ami.RemoveBundle)
