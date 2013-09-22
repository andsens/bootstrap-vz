

def tasks(tasklist, manifest):
	from user_packages import AddUserPackages, AddLocalUserPackages
	tasklist.add(AddUserPackages,
	             AddLocalUserPackages)
