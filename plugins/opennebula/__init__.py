

def resolve_tasks(taskset, manifest):
	import tasks
	taskset.add(tasks.OpenNebulaContext)
