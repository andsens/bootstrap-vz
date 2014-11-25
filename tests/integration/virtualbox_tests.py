import tools
from manifests import partials
from . import build_settings


def test_virtualbox_unpartitioned_extlinux():
	import yaml
	specific_settings = yaml.load("""
provider:
  name: virtualbox
  guest_additions: {guest_additions}
system:
  bootloader: extlinux
volume:
  backing: vdi
  partitions:
    type: msdos
""".format(guest_additions=build_settings['virtualbox']['guest_additions']))
	manifest = tools.merge_dicts(partials['base'], partials['stable64'],
	                             partials['unpartitioned'], specific_settings)

	image = tools.bootstrap(manifest)
	instance = image.create_instance()
	instance.boot()

	tools.test_instance(instance)

	instance.destroy()
	image.destroy()
