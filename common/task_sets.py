from common.tasks import workspace
from common.tasks import packages
from common.tasks import host
from common.tasks import volume
from common.tasks import filesystem
from common.tasks import partitioning
from common.tasks import cleanup
from common.tasks import apt
from common.tasks import security
from common.tasks import locale

base_set = [workspace.CreateWorkspace,
            packages.HostPackages,
            packages.ImagePackages,
            host.CheckPackages,
            workspace.DeleteWorkspace,
            ]

volume_set = [volume.Attach,
              volume.Detach,
              ]

partitioning_set = [partitioning.PartitionVolume,
                    partitioning.MapPartitions,
                    partitioning.UnmapPartitions,
                    ]

boot_partition_set = [filesystem.CreateBootMountDir,
                      filesystem.MountBoot,
                      filesystem.UnmountBoot,
                      ]

mounting_set = [filesystem.CreateMountDir,
                filesystem.MountRoot,
                filesystem.MountSpecials,
                filesystem.UnmountSpecials,
                filesystem.UnmountRoot,
                filesystem.DeleteMountDir,
                ]

ssh_set = [security.DisableSSHPasswordAuthentication,
           security.DisableSSHDNSLookup,
           cleanup.ShredHostkeys,
           ]

apt_set = [apt.DisableDaemonAutostart,
           apt.AptSources,
           apt.AptUpgrade,
           apt.PurgeUnusedPackages,
           apt.AptClean,
           apt.EnableDaemonAutostart,
           ]

locale_set = [locale.GenerateLocale,
              locale.SetTimezone,
              ]


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
