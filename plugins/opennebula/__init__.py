import tasks


def resolve_tasks(taskset, manifest):
	taskset.add(tasks.AddONEContextPackage)
	taskset.add(tasks.OpenNebulaContext)
