

def init_subparser(subparsers):
	cmd = subparsers.add_parser('ec2', help='Bootstrap Debian for EC2')
	cmd.add_argument('--access-key', help='AWS Access Key', metavar='ID')
	cmd.add_argument('--secret-key', help='AWS Secret Key', metavar='KEY')
	cmd.add_argument('manifest', help='Manifest file to use for bootstrapping', metavar='MANIFEST')
	cmd.set_defaults(func=run)


def run(args):
	from manifest import Manifest
	from common import BootstrapInformation
	manifest = Manifest(args.manifest)
	manifest.validate()

	task_list = get_tasklist(manifest)

	info = BootstrapInformation(manifest=manifest, args=args)
	task_list.run(info)


def get_tasklist(manifest):
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
