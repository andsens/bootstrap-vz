import tools
from manifests import partials
from bootstrapvz.base.manifest import Manifest
from bootstrapvz.remote.build_servers import pick_build_server
from . import build_servers
from images.virtualbox import VirtualBoxImage
from instances.virtualbox import VirtualBoxInstance


def test_virtualbox_unpartitioned_extlinux():
	import yaml
	manifest_data = yaml.load("""
provider:
  name: virtualbox
system:
  bootloader: extlinux
volume:
  backing: vdi
  partitions:
    type: msdos
""")
	manifest_data = tools.merge_dicts(partials['base'], partials['stable64'], partials['unpartitioned'],
	                                  partials['root_password'], partials['apt_proxy'],
	                                  manifest_data)

	build_server = pick_build_server(build_servers, manifest_data)
	manifest_data = build_server.apply_build_settings(manifest_data)
	manifest = Manifest(data=manifest_data)

	# bootstrap_info = tools.bootstrap(manifest, build_server)
	from bootstrapvz.base.bootstrapinfo import BootstrapInformation
	bootstrap_info = BootstrapInformation(manifest)
	bootstrap_info.volume.image_path = '/target/debian-wheezy-amd64-141218.vdi'

	from bootstrapvz.remote.build_servers import LocalBuildServer
	if isinstance(build_server, LocalBuildServer):
		image_path = bootstrap_info.volume.image_path
	else:
		# import tempfile
		# handle, image_path = tempfile.mkstemp()
		# import os
		# os.close(handle)
		# build_server.download(bootstrap_info.volume.image_path, image_path)
		# build_server.delete(bootstrap_info.volume.image_path)
		image_path = '/Users/anders/Workspace/cloud/images/debian-wheezy-amd64-141130.vmdk'

	image = VirtualBoxImage(manifest, image_path)
	output = None
	try:
		instance = VirtualBoxInstance('unpartitioned_extlinux', image)
		try:
			instance.create()
			try:
				instance.boot()
				output = instance.get_console_output()
				# tools.reachable_with_ssh(instance)
			finally:
				instance.shutdown()
		finally:
			instance.destroy()
	finally:
		image.destroy()
		import os
		os.remove(image_path)
