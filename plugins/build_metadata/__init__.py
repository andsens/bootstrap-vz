

def resolve_tasks(taskset, manifest):
	from tasks import WriteMetadata
	taskset.add(WriteMetadata)
