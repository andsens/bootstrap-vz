

def initialize_image(manifest, build_server, bootstrap_info):
	if manifest.provider['name'] == 'virtualbox':
		import vbox
		return vbox.initialize_image(manifest, build_server, bootstrap_info)
	if manifest.provider['name'] == 'ec2':
		import ami
		credentials = {'access-key': build_server.build_settings['ec2-credentials']['access-key'],
		               'secret-key': build_server.build_settings['ec2-credentials']['secret-key']}
		return ami.initialize_image(manifest, credentials, bootstrap_info)
