import tasks


def resolve_tasks(taskset, manifest):
	taskset.update([tasks.AddFolderMounts,
	                tasks.RemoveFolderMounts,
	                ])


def resolve_rollback_tasks(taskset, manifest, counter_task):
	counter_task(tasks.AddFolderMounts, tasks.RemoveFolderMounts)
