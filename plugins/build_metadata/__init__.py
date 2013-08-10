

def tasks(tasklist, manifest):
	from tasks import WriteMetadata
	tasklist.add(WriteMetadata())
