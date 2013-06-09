from base import Task


class GetCredentials(Task):
	description = 'Getting AWS credentials'

	def run(self, info):
		super(GetCredentials, self).run(info)
		info.ec2_credentials = self.get_ec2_credentials(info.manifest)

	def get_ec2_credentials(self, manifest):
		from os import getenv
		# manifest overrides environment
		if(manifest.credentials['access-key'] and manifest.credentials['secret-key']):
			return {'access_key': manifest.credentials['access-key'],
			        'secret_key': manifest.credentials['secret-key']}
		if(getenv('EC2_ACCESS_KEY') and getenv('EC2_SECRET_KEY')):
			return {'access_key': getenv('EC2_ACCESS_KEY'),
			        'secret_key': getenv('EC2_SECRET_KEY')}

		if(bool(manifest.credentials['access-key']) != bool(manifest.credentials['secret-key'])):
			raise RuntimeError('Both the access key and secret key must be specified in the manifest.')
		if(bool(getenv('EC2_ACCESS_KEY')) != bool(getenv('EC2_SECRET_KEY'))):
			raise RuntimeError('Both the access key and secret key must be specified as environment variables.')

		raise RuntimeError('No ec2 credentials found.')


class Connect(Task):
	description = 'Connecting to EC2'
	
	def run(self, info):
		super(Connect, self).run(info)
		# import boto.ec2
		# info.ec2_connection = boto.ec2.connect_to_region(info.host['region'],
		#                                                  aws_access_key_id=info.ec2_credentials['access_key'],
		#                                                  aws_secret_access_key=info.ec2_credentials['secret_key'])
		# return 'ec2_connection', ec2_connection
