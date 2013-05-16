

def modify_tasklist(tasklist, manifest):
	from providers.ec2.packages import ImagePackages
	from adminuser import AddSudoPackage
	tasklist.after(ImagePackages, AddSudoPackage())
