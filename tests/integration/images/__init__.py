

def initialize_image(manifest, build_server, bootstrap_info):
	if manifest.provider['name'] == 'virtualbox':
		import vbox
		return vbox.initialize_image(manifest, build_server, bootstrap_info)
