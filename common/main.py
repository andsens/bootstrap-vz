from providers import providers


def main():
	from argparse import ArgumentParser
	parser = ArgumentParser(description='Bootstrap Debian for the cloud.')
	parser.add_argument('--debug', action='store_true',
	                    help='Print debugging information')
	parser.set_defaults(func=run)

	subparsers = parser.add_subparsers(title='providers', description='supported providers', dest='provider')

	for provider in providers.values():
		provider.init_subparser(subparsers)

	args = parser.parse_args()
	args.func(args)


def run(args):
	provider = providers[args.provider]
	manifest = provider.Manifest(args.manifest)
	manifest.validate()
	manifest.load_plugins()

	tasklist = provider.tasklist(manifest)
	tasklist.plugins(manifest)

	from common import BootstrapInformation
	bootstrap_info = BootstrapInformation(manifest, args)
	tasklist.run(bootstrap_info)
