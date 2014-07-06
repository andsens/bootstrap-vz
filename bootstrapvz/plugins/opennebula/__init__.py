import tasks


def resolve_tasks(taskset, manifest):
	from bootstrapvz.common.tools import get_codename
	if get_codename(manifest.system['release']) == 'wheezy':
		taskset.add(tasks.AddBackports)
	taskset.update([tasks.AddONEContextPackage])
