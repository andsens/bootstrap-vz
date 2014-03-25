from common.tasks import workspace
from common.tasks import packages
from common.tasks import host
from common.tasks import boot
from common.tasks import bootstrap
from common.tasks import volume
from common.tasks import filesystem
from common.tasks import partitioning
from common.tasks import cleanup
from common.tasks import apt
from common.tasks import security
from common.tasks import locale

base_set = [workspace.CreateWorkspace,
            bootstrap.AddRequiredCommands,
            host.CheckExternalCommands,
            bootstrap.Bootstrap,
            workspace.DeleteWorkspace,
            ]

volume_set = [volume.Attach,
              volume.Detach,
              filesystem.AddRequiredCommands,
              filesystem.Format,
              filesystem.FStab,
              ]

partitioning_set = [partitioning.AddRequiredCommands,
                    partitioning.PartitionVolume,
                    partitioning.MapPartitions,
                    partitioning.UnmapPartitions,
                    ]

boot_partition_set = [filesystem.CreateBootMountDir,
                      filesystem.MountBoot,
                      ]

mounting_set = [filesystem.CreateMountDir,
                filesystem.MountRoot,
                filesystem.MountSpecials,
                filesystem.UnmountRoot,
                filesystem.DeleteMountDir,
                ]

ssh_set = [security.DisableSSHPasswordAuthentication,
           security.DisableSSHDNSLookup,
           cleanup.ShredHostkeys,
           ]


def get_apt_set(manifest):
	base = [apt.AddDefaultSources,
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
		base.append(apt.AddManifestSources)
	if 'trusted-keys' in manifest.packages:
		base.append(apt.InstallTrustedKeys)
	if 'install' in manifest.packages:
		base.append(packages.AddManifestPackages)
	return base


locale_set = [locale.LocaleBootstrapPackage,
              locale.GenerateLocale,
              locale.SetTimezone,
              ]


bootloader_set = {'grub':     [boot.AddGrubPackage, boot.InstallGrub],
                  'extlinux': [boot.AddExtlinuxPackage, boot.InstallExtLinux],
                  }


def get_fs_specific_set(partitions):
	task_set = {'ext2': [filesystem.TuneVolumeFS],
	            'ext3': [filesystem.TuneVolumeFS],
	            'ext4': [filesystem.TuneVolumeFS],
	            'xfs':  [filesystem.AddXFSProgs],
	            }
	tasks = set()
	if 'boot' in partitions:
		tasks.update(task_set.get(partitions['boot']['filesystem'], []))
	if 'root' in partitions:
		tasks.update(task_set.get(partitions['root']['filesystem'], []))
	return tasks
