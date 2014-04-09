import tasks


def resolve_tasks(taskset, manifest):
	if manifest.system['release'] in ['wheezy', 'stable']:
		taskset.add(tasks.AddBackports)
	taskset.update([tasks.AddONEContextPackage])
