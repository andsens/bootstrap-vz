import tools
from manifests import partials


def test_virtualbox_unpartitioned_extlinux():
	import yaml
	specific_settings = yaml.load("""
provider:
  name: virtualbox
system:
  bootloader: extlinux
volume:
  backing: vdi
  partitions:
    type: msdos
""")
	manifest = tools.merge_dicts(partials['base'], partials['stable64'],
	                             partials['unpartitioned'], specific_settings)

	build_server = tools.pick_build_server(manifest)
	manifest['provider']['guest_additions'] = build_server.build_settings['guest_additions']

	bootstrap_info = tools.bootstrap(manifest, build_server)

	if isinstance(build_server, tools.build_servers.LocalBuildServer):
		image_path = bootstrap_info.volume.image_path
	else:
		import tempfile
		handle, image_path = tempfile.mkstemp()
		handle.close()
		build_server.download(bootstrap_info.volume.image_path, image_path)
		build_server.delete(bootstrap_info.volume.image_path)

	try:
		image = tools.images.VirtualBoxImage(manifest, image_path)

		instance = tools.instances.VirtualBoxInstance(image)
		instance.create()
		instance.boot()

		tools.test(instance)
	finally:
		if 'instance' in locals():
			instance.destroy()
		if 'image' in locals():
			image.destroy()
