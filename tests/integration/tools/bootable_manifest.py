from bootstrapvz.remote.build_servers import LocalBuildServer
from ..images.virtualbox import VirtualBoxImage


class BootableManifest(object):

	def __init__(self, manifest_data):
		self.manifest_data = manifest_data

	def pick_build_server(self, path='build-servers.yml'):
		from bootstrapvz.common.tools import load_data
		build_servers = load_data(path)
		from bootstrapvz.remote.build_servers import pick_build_server
		return pick_build_server(build_servers, self.manifest_data)

	def get_manifest(self, build_server):
		manifest_data = build_server.apply_build_settings(self.manifest_data)
		from bootstrapvz.base.manifest import Manifest
		return Manifest(data=manifest_data)

	def bootstrap(self, manifest, build_server):
		if isinstance(build_server, LocalBuildServer):
			from bootstrapvz.base.main import run
			bootstrap_info = run(manifest)
		else:
			from bootstrapvz.remote.main import run
			bootstrap_info = run(manifest, build_server)
		return bootstrap_info

	def get_image(self, build_server, bootstrap_info, manifest):
		if isinstance(build_server, LocalBuildServer):
			image_path = bootstrap_info.volume.image_path
		else:
			import tempfile
			handle, image_path = tempfile.mkstemp()
			import os
			os.close(handle)
			build_server.download(bootstrap_info.volume.image_path, image_path)
			build_server.delete(bootstrap_info.volume.image_path)
		image_type = {'virtualbox': VirtualBoxImage}
		return image_type.get(self.manifest_data['provider']['name'])(manifest, image_path)

	def __enter__(self):
		self.build_server = self.pick_build_server()
		self.manifest = self.get_manifest(self.build_server)
		self.bootstrap_info = self.bootstrap(self.manifest, self.build_server)
		self.image = self.get_image(self.build_server, self.bootstrap_info, self.manifest)
		self.image.open()
		self.instance = self.image.get_instance()
		self.instance.up()
		return self.instance

	def __exit__(self, type, value, traceback):
		if hasattr(self, 'instance'):
			self.instance.down()
		if hasattr(self, 'image'):
			self.image.close()
