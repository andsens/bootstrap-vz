

class BuildServer(object):

	def __init__(self, name, settings):
		self.name = name
		self.settings = settings
		self.build_settings = settings.get('build_settings', {})
		self.can_bootstrap = settings['can_bootstrap']
		self.release = settings.get('release', None)

	def apply_build_settings(self, manifest_data):
		if manifest_data['provider']['name'] == 'virtualbox' and 'guest_additions' in manifest_data['provider']:
			manifest_data['provider']['guest_additions'] = self.build_settings['guest_additions']
		if 'apt_proxy' in self.build_settings:
			manifest_data.get('plugins', {})['apt_proxy'] = self.build_settings['apt_proxy']
		return manifest_data
