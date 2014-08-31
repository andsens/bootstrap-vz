import tools
from . import manifests
from . import build_settings


def test_virtualbox_unpartitioned_extlinux():
	specific_settings = {}
	specific_settings['provider'] = {'name': 'virtualbox',
	                                 'guest_additions': build_settings['virtualbox']['guest_additions']}
	specific_settings['system'] = {'release': 'wheezy',
	                               'architecture': 'amd64',
	                               'bootloader': 'extlinux'}
	specific_settings['volume'] = {'backing': 'vdi',
	                               'partitions': {'type': 'msdos'}}
	manifest = tools.merge_dicts(manifests['base'], manifests['unpartitioned'], specific_settings)

	client = tools.get_client(build_settings['virtualbox'])

	image = client.bootstrap(manifest, build_settings['virtualbox'])
	instance = image.create_instance()
	instance.boot()

	tools.test_instance(instance, build_settings['virtualbox'])

	instance.destroy()
	image.destroy()

	client.shutdown()
