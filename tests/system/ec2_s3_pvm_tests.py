from manifests import merge_manifest_data
from tools import boot_manifest
import random

s3_bucket_name = '{id:x}'.format(id=random.randrange(16 ** 16))
partials = {'s3_pvm': '''
provider:
  name: ec2
  virtualization: pvm
  description: Debian {system.release} {system.architecture}
  bucket: ''' + s3_bucket_name + '''
system: {bootloader: pvgrub}
volume: {backing: s3}
'''
            }


def test_unpartitioned_oldstable():
    std_partials = ['base', 'oldstable64', 'unpartitioned', 'root_password']
    custom_partials = [partials['s3_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 'm1.small'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_unpartitioned_stable():
    std_partials = ['base', 'stable64', 'unpartitioned', 'root_password']
    custom_partials = [partials['s3_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 'm1.small'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)


def test_unpartitioned_unstable():
    std_partials = ['base', 'unstable64', 'unpartitioned', 'root_password']
    custom_partials = [partials['s3_pvm']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    boot_vars = {'instance_type': 'm1.small'}
    with boot_manifest(manifest_data, boot_vars) as instance:
        print(instance.get_console_output().output)
