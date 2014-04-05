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
	if manifest.packages.get('install_standard', False):
		base.append(packages.AddTaskselStandardPackages)
	return base


locale_set = [locale.LocaleBootstrapPackage,
              locale.GenerateLocale,
              locale.SetTimezone,
              ]


bootloader_set = {'grub':     [boot.AddGrubPackage, boot.ConfigureGrub, boot.InstallGrub],
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
