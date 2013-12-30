import tasks


def resolve_tasks(tasklist, manifest):
	tasklist.add(tasks.AddFolderMounts,
	             tasks.RemoveFolderMounts)


def resolve_rollback_tasks(tasklist, tasks_completed, manifest):
	completed = [type(task) for task in tasks_completed]

	def counter_task(task, counter):
		if task in completed and counter not in completed:
			tasklist.add(counter)

	counter_task(tasks.AddFolderMounts, tasks.RemoveFolderMounts)
