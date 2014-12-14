import tools
import tools.images
import tools.instances
from manifests import partials
from bootstrapvz.base.manifest import Manifest
from bootstrapvz.remote.build_servers import pick_build_server
from . import build_servers


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
	manifest_data = tools.merge_dicts(partials['base'], partials['stable64'],
	                                  partials['unpartitioned'], manifest_data)

	build_server = pick_build_server(build_servers, manifest_data)
	manifest_data = build_server.apply_build_settings(manifest_data)
	manifest = Manifest(data=manifest_data)

	bootstrap_info = tools.bootstrap(manifest, build_server)

	from bootstrapvz.remote.build_servers import LocalBuildServer
	if isinstance(build_server, LocalBuildServer):
		image_path = bootstrap_info.volume.image_path
	else:
		import tempfile
		handle, image_path = tempfile.mkstemp()
		import os
		os.close(handle)
		build_server.download(bootstrap_info.volume.image_path, image_path)
		build_server.delete(bootstrap_info.volume.image_path)

	try:
		image = tools.images.VirtualBoxImage(manifest, image_path)
		try:
			instance = tools.instances.VirtualBoxInstance('unpartitioned_extlinux', image)
			instance.create()
			# instance.boot()

			# tools.test(instance)

		finally:
			if 'instance' in locals():
				instance.destroy()
	finally:
		if 'image' in locals():
			image.destroy()
		import os
		os.remove(image_path)
