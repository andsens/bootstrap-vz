

def main():
	from argparse import ArgumentParser
	parser = ArgumentParser(description='Bootstrap Debian for the cloud.')
	parser.add_argument('--debug', action='store_true',
	                    help='Print debugging information')
	parser.add_argument('manifest', help='Manifest file to use for bootstrapping', metavar='MANIFEST')
	parser.set_defaults(func=run)

	args = parser.parse_args()
	args.func(args)


def run(args):
	from manifest import load_manifest
	from manifest import get_provider
	data     = load_manifest(args.manifest)
	provider = get_provider(data)
	manifest = provider.Manifest(args.manifest, data)
	
	manifest.validate()
	manifest.load_plugins()

	tasklist = provider.tasklist(manifest)
	tasklist.plugins(manifest)

	from common import BootstrapInformation
	bootstrap_info = BootstrapInformation(manifest=manifest, debug=args.debug)
	tasklist.run(bootstrap_info)
