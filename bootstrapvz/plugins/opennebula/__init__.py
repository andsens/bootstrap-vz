

def resolve_tasks(taskset, manifest):
	import tasks
	from bootstrapvz.common.tasks import apt
	from bootstrapvz.common.tools import get_codename
	if get_codename(manifest.system['release']) == 'wheezy':
		taskset.add(apt.AddBackports)
	taskset.update([tasks.AddONEContextPackage])
