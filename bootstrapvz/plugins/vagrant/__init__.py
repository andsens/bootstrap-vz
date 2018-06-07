from . import tasks
from bootstrapvz.common import task_groups
from bootstrapvz.common.tasks import image, ssh, volume
from bootstrapvz.common.tools import rel_path


def validate_manifest(data, validator, error):
    validator(data, rel_path(__file__, 'manifest-schema.yml'))
    vagrant_provider = data['plugins']['vagrant'].get('provider', 'virtualbox')
    if vagrant_provider == 'virtualbox' and data['volume']['backing'] != 'vmdk':
        error('Virtualbox vagrant boxes support vmdk images only', ['plugins', 'vagrant', 'provider'])
    if vagrant_provider == 'libvirt' and data['volume']['backing'] != 'qcow2':
        error('Libvirt vagrant boxes support qcow2 images only', ['plugins', 'vagrant', 'provider'])


def resolve_tasks(taskset, manifest):
    taskset.update(task_groups.ssh_group)

    taskset.discard(image.MoveImage)
    taskset.discard(ssh.DisableSSHPasswordAuthentication)

    taskset.update([tasks.CheckBoxPath,
                    tasks.CreateVagrantBoxDir,
                    tasks.AddPackages,
                    tasks.CreateVagrantUser,
                    tasks.PasswordlessSudo,
                    tasks.SetRootPassword,
                    tasks.AddInsecurePublicKey,
                    tasks.PackageBox,
                    tasks.RemoveVagrantBoxDir,
                    volume.Delete,
                    ])


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    counter_task(taskset, tasks.CreateVagrantBoxDir, tasks.RemoveVagrantBoxDir)
