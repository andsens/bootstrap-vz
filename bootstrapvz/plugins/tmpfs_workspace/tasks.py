from os import makedirs, rmdir

from bootstrapvz.base import Task
from bootstrapvz.common.tasks.workspace import CreateWorkspace, DeleteWorkspace
from bootstrapvz.common import phases
from bootstrapvz.common.tools import log_check_call


class CreateTmpFsWorkspace(Task):
    description = 'Creating directory for tmpfs-based workspace'
    phase = phases.preparation

    @classmethod
    def run(cls, info):
        makedirs(info.workspace)


class MountTmpFsWorkspace(Task):
    description = 'Mounting tmpfs-based workspace'
    phase = phases.preparation

    # CreateWorkspace is explicitly skipped (see the plugin's resolve_task function). Several other tasks
    # depend on CreateWorkspace to put their own files inside the workspace. We position MountTmpFs before
    # CreateWorkspace to leverage these dependencies. See also UnmountTmpFs/DeleteWorkspace below.
    successors = [CreateWorkspace]
    predecessors = [CreateTmpFsWorkspace]

    @classmethod
    def run(cls, info):
        log_check_call(['mount', '--types', 'tmpfs', 'none', info.workspace])


class UnmountTmpFsWorkspace(Task):
    description = 'Unmounting tmpfs-based workspace'
    phase = phases.cleaning
    predecessors = [DeleteWorkspace]

    @classmethod
    def run(cls, info):
        log_check_call(['umount', info.workspace])


class DeleteTmpFsWorkspace(Task):
    description = 'Deleting directory for tmpfs-based workspace'
    phase = phases.cleaning
    predecessors = [UnmountTmpFsWorkspace]

    @classmethod
    def run(cls, info):
        rmdir(info.workspace)
