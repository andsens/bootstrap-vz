from tasks import workspace
from tasks import packages
from tasks import host
from tasks import boot
from tasks import bootstrap
from tasks import volume
from tasks import filesystem
from tasks import partitioning
from tasks import cleanup
from tasks import apt
from tasks import security
from tasks import locale
from tasks import network
from tasks import initd
from tasks import ssh


def get_standard_groups(manifest):
	group = []
	group.extend(get_base_group(manifest))
	group.extend(volume_group)
	if manifest.volume['partitions']['type'] != 'none':
		group.extend(partitioning_group)
	if 'boot' in manifest.volume['partitions']:
		group.extend(boot_partition_group)
	group.extend(mounting_group)
	group.extend(get_fs_specific_group(manifest))
	group.extend(get_network_group(manifest))
	group.extend(get_apt_group(manifest))
	group.extend(security_group)
	group.extend(locale_group)
	group.extend(bootloader_group.get(manifest.system['bootloader'], []))
	group.extend(cleanup_group)
	return group


def get_base_group(manifest):
	group = [workspace.CreateWorkspace,
	         bootstrap.AddRequiredCommands,
	         host.CheckExternalCommands,
	         bootstrap.Bootstrap,
	         workspace.DeleteWorkspace,
	         ]
	if manifest.bootstrapper.get('tarball', False):
		group.append(bootstrap.MakeTarball)
	return group


volume_group = [volume.Attach,
                volume.Detach,
                filesystem.AddRequiredCommands,
                filesystem.Format,
                filesystem.FStab,
                ]

partitioning_group = [partitioning.AddRequiredCommands,
                      partitioning.PartitionVolume,
                      partitioning.MapPartitions,
                      partitioning.UnmapPartitions,
                      ]

boot_partition_group = [filesystem.CreateBootMountDir,
                        filesystem.MountBoot,
                        ]

mounting_group = [filesystem.CreateMountDir,
                  filesystem.MountRoot,
                  filesystem.MountSpecials,
                  filesystem.UnmountRoot,
                  filesystem.DeleteMountDir,
                  ]

ssh_group = [ssh.AddOpenSSHPackage,
             ssh.DisableSSHPasswordAuthentication,
             ssh.DisableSSHDNSLookup,
             ssh.AddSSHKeyGeneration,
             initd.InstallInitScripts,
             ssh.ShredHostkeys,
             ]


def get_network_group(manifest):
	group = [network.ConfigureNetworkIF,
	         network.RemoveDNSInfo]
	if manifest.system.get('hostname', False):
		group.append(network.SetHostname)
	else:
		group.append(network.RemoveHostname)
	return group


def get_apt_group(manifest):
	group = [apt.AddDefaultSources,
	         apt.WriteSources,
	         apt.DisableDaemonAutostart,
	         apt.AptUpdate,
	         apt.AptUpgrade,
	         packages.InstallPackages,
	         apt.PurgeUnusedPackages,
	         apt.AptClean,
	         apt.EnableDaemonAutostart,
	         ]
	if 'sources' in manifest.packages:
		group.append(apt.AddManifestSources)
	if 'trusted-keys' in manifest.packages:
		group.append(apt.InstallTrustedKeys)
	if 'preferences' in manifest.packages:
		group.append(apt.AddManifestPreferences)
		group.append(apt.WritePreferences)
	if 'install' in manifest.packages:
		group.append(packages.AddManifestPackages)
	if manifest.packages.get('install_standard', False):
		group.append(packages.AddTaskselStandardPackages)
	return group

security_group = [security.EnableShadowConfig]

locale_group = [locale.LocaleBootstrapPackage,
                locale.GenerateLocale,
                locale.SetTimezone,
                ]


bootloader_group = {'grub':     [boot.AddGrubPackage, boot.ConfigureGrub, boot.InstallGrub],
                    'extlinux': [boot.AddExtlinuxPackage, boot.InstallExtLinux],
                    }


def get_fs_specific_group(manifest):
	partitions = manifest.volume['partitions']
	fs_specific_tasks = {'ext2': [filesystem.TuneVolumeFS],
	                     'ext3': [filesystem.TuneVolumeFS],
	                     'ext4': [filesystem.TuneVolumeFS],
	                     'xfs':  [filesystem.AddXFSProgs],
	                     }
	group = set()
	if 'boot' in partitions:
		group.update(fs_specific_tasks.get(partitions['boot']['filesystem'], []))
	if 'root' in partitions:
		group.update(fs_specific_tasks.get(partitions['root']['filesystem'], []))
	return list(group)


cleanup_group = [cleanup.ClearMOTD,
                 cleanup.CleanTMP,
                 ]
