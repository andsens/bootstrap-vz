

def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)
	if ('password' in data['plugins']['admin_user'] and 'pubkey' in data['plugins']['admin_user']):
		msg = 'passwd and pubkey are mutually exclusive.'
		error(msg, ['plugins', 'admin_user'])
	if 'pubkey' in data['plugins']['admin_user']:
		full_path = data['plugins']['admin_user']['pubkey']
		if not os.path.exists(full_path):
	    		msg = 'Could not find public key at %s' % full_path
	    		error(msg, ['plugins', 'admin_user'])


def resolve_tasks(taskset, manifest):
	import tasks
	from bootstrapvz.common.tasks import ssh

	from bootstrapvz.common.releases import jessie
	if manifest.release < jessie:
		taskset.update([ssh.DisableRootLogin])

	if 'password' in manifest.plugins['admin_user']:
		taskset.discard(ssh.DisableSSHPasswordAuthentication)
		taskset.add(tasks.AdminUserCredentialsPassword)
	else:
		if 'pubkey' in manifest.plugins['admin_user']:
			taskset.add(tasks.AdminUserCredentialsPublicKey)
		else:
			taskset.add(tasks.AdminUserCredentialsEc2)

	taskset.update([tasks.AddSudoPackage,
	                tasks.CreateAdminUser,
	                tasks.PasswordlessSudo,
	                ])
