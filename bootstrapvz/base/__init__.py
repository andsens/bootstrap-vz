from phase import Phase
from task import Task
from main import main

__all__ = ['Phase', 'Task', 'main']


def validate_manifest(data, validator, error):
    """Validates the manifest using the base manifest

    :param dict data: The data of the manifest
    :param function validator: The function that validates the manifest given the data and a path
    :param function error: The function tha raises an error when the validation fails
    """
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))

    from bootstrapvz.common.releases import get_release, squeeze
    release = get_release(data['system']['release'])

    if release < squeeze:
        error('Only Debian squeeze and later is supported', ['system', 'release'])

    # Check the bootloader/partitioning configuration.
    # Doing this via the schema is a pain and does not output a useful error message.
    if data['system']['bootloader'] == 'grub':

        if data['volume']['partitions']['type'] == 'none':
            error('Grub cannot boot from unpartitioned disks', ['system', 'bootloader'])

        if release == squeeze:
            error('Grub installation on squeeze is not supported', ['system', 'bootloader'])

    # Check the provided apt.conf(5) options
    if 'packages' in data:
        for name, val in data['packages'].get('apt.conf.d', {}).iteritems():
            from bootstrapvz.common.tools import log_call

            status, _, _ = log_call(['apt-config', '-c=/dev/stdin', 'dump'],
                                    stdin=val + '\n')

            if status != 0:
                error('apt.conf(5) syntax error', ['packages', 'apt.conf.d', name])
