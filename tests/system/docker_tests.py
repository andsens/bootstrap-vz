from manifests import merge_manifest_data
from tools import boot_manifest

partials = {'docker': '''
provider:
  name: docker
  virtualization: hvm
  dockerfile: CMD /bin/bash
bootstrapper:
  variant: minbase
system:
  bootloader: none
volume:
  backing: folder
  partitions:
    type: none
    root:
      filesystem: ext4
      size: 1GiB
''',
            }


def test_stable():
    std_partials = ['base', 'stable64']
    custom_partials = [partials['docker']]
    manifest_data = merge_manifest_data(std_partials, custom_partials)
    with boot_manifest(manifest_data) as instance:
        print('\n'.join(instance.run(['echo', 'test'])))
