

def tasks(tasklist, manifest):
	from opennebula import OpenNebulaContext
	tasklist.add(OpenNebulaContext())
