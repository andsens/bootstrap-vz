from bootstrapvz.base import Task
from bootstrapvz.common import phases

import os
import shutil


def modify_path(info, path, entry):
    from bootstrapvz.common.tools import log_check_call
    if 'permissions' in entry:
        # We wrap the permissions string in str() in case
        #  the user specified a numeric bitmask
        chmod_command = ['chroot', info.root, 'chmod', str(entry['permissions']), path]
        log_check_call(chmod_command)

    if 'owner' in entry:
        chown_command = ['chroot', info.root, 'chown', entry['owner'], path]
        log_check_call(chown_command)

    if 'group' in entry:
        chgrp_command = ['chroot', info.root, 'chgrp', entry['group'], path]
        log_check_call(chgrp_command)


class MkdirCommand(Task):
    description = 'Creating directories requested by user'
    phase = phases.user_modification

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import log_check_call

        for dir_entry in info.manifest.plugins['file_copy']['mkdirs']:
            mkdir_command = ['chroot', info.root, 'mkdir', '-p', dir_entry['dir']]
            log_check_call(mkdir_command)
            modify_path(info, dir_entry['dir'], dir_entry)


class ValidateFiles(Task):
    description = 'Check that the required files exist'
    phase = phases.validation

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import rel_path

        for i, file_entry in enumerate(info.manifest.plugins['file_copy']['files']):
            if not os.path.exists(rel_path(info.manifest.path, file_entry['src'])):
                msg = 'The source file %s does not exist.' % file_entry['src']
                info.manifest.validation_error(msg, ['plugins', 'file_copy', 'files', i])


class FileCopyCommand(Task):
    description = 'Copying user specified files into the image'
    phase = phases.user_modification
    predecessors = [MkdirCommand]

    @classmethod
    def run(cls, info):
        from bootstrapvz.common.tools import rel_path

        for file_entry in info.manifest.plugins['file_copy']['files']:
            # note that we don't use os.path.join because it can't
            #  handle absolute paths, which 'dst' most likely is.
            final_destination = os.path.normpath("%s/%s" % (info.root, file_entry['dst']))
            src_path = rel_path(info.manifest.path, file_entry['src'])
            if os.path.isfile(src_path):
                shutil.copy(src_path, final_destination)
            else:
                shutil.copytree(src_path, final_destination)

            modify_path(info, file_entry['dst'], file_entry)
