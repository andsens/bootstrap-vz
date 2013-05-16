from common import Task


class GetCredentials(Task):
	def run(self, info):
		super(GetCredentials, self).run(info)
		info.ec2_credentials = self.get_ec2_credentials(info.args, info.manifest)

	def get_ec2_credentials(self, args, manifest):
		from os import getenv
		# args override manifest override environment
		if(args.access_key and args.secret_key):
			return {'access_key': args.access_key,
			        'secret_key': args.secret_key}
		if(manifest.credentials['access-key'] and manifest.credentials['secret-key']):
			return {'access_key': manifest.credentials['access-key'],
			        'secret_key': manifest.credentials['secret-key']}
		if(getenv('EC2_ACCESS_KEY') and getenv('EC2_SECRET_KEY')):
			return {'access_key': getenv('EC2_ACCESS_KEY'),
			        'secret_key': getenv('EC2_SECRET_KEY')}

		if(bool(args.access_key) != bool(args.secret_key)):
			raise RuntimeError('Both the access key and secret key must be specified as arguments.')
		if(bool(manifest.credentials['access-key']) != bool(manifest.credentials['secret-key'])):
			raise RuntimeError('Both the access key and secret key must be specified in the manifest.')
		if(bool(getenv('EC2_ACCESS_KEY')) != bool(getenv('EC2_SECRET_KEY'))):
			raise RuntimeError('Both the access key and secret key must be specified as environment variables.')

		raise RuntimeError('No ec2 credentials found.')


class Connect(Task):
	def run(self, info):
		super(Connect, self).run(info)
		# import boto.ec2
		# info.ec2_connection = boto.ec2.connect_to_region(info.host['region'],
		#                                                  aws_access_key_id=info.ec2_credentials['access_key'],
		#                                                  aws_secret_access_key=info.ec2_credentials['secret_key'])
		# return 'ec2_connection', ec2_connection
