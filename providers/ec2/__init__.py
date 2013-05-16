from manifest import Manifest


def init_subparser(subparsers):
	sub = subparsers.add_parser('ec2', help='Bootstrap Debian for EC2')
	sub.add_argument('--access-key', help='AWS Access Key', metavar='ID')
	sub.add_argument('--secret-key', help='AWS Secret Key', metavar='KEY')
	sub.add_argument('manifest', help='Manifest file to use for bootstrapping', metavar='MANIFEST')


def tasklist(manifest):
	from common import TaskList
	import packages
	import ec2
	import host
	task_list = TaskList()
	task_list.extend([packages.HostPackages(),
	                  packages.ImagePackages(),
	                  ec2.GetCredentials(),
	                  host.GetInfo(),
	                  ec2.Connect(),
	                  host.InstallPackages()
                   ])

	return task_list
