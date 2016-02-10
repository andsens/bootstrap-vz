

def validate_manifest(data, validator, error):
	import os.path
	schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
	validator(data, schema_path)
	pubkey = data['plugins']['admin_user'].get('pubkey', None)
	if pubkey is not None and not os.path.exists(pubkey):
		msg = 'Could not find public key at %s' % pubkey
		error(msg, ['plugins', 'admin_user', 'pubkey'])


def resolve_tasks(taskset, manifest):
	import tasks
	from bootstrapvz.common.tasks import ssh

	from bootstrapvz.common.releases import jessie
	if manifest.release < jessie:
		taskset.update([ssh.DisableRootLogin])

	if 'password' in manifest.plugins['admin_user']:
		taskset.discard(ssh.DisableSSHPasswordAuthentication)
		taskset.add(tasks.AdminUserCredentialsPassword)
	if 'pubkey' in manifest.plugins['admin_user']:
		taskset.add(tasks.AdminUserCredentialsPublicKey)
	else:
		taskset.add(tasks.AdminUserCredentialsEc2)

	taskset.update([tasks.AddSudoPackage,
	                tasks.CreateAdminUser,
	                tasks.PasswordlessSudo,
	                ])
