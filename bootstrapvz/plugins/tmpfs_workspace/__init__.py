from bootstrapvz.common.tasks.workspace import CreateWorkspace, DeleteWorkspace
from .tasks import CreateTmpFsWorkspace, MountTmpFsWorkspace, UnmountTmpFsWorkspace, DeleteTmpFsWorkspace


def resolve_tasks(taskset, manifest):
    taskset.discard(CreateWorkspace)
    taskset.discard(DeleteWorkspace)

    taskset.add(CreateTmpFsWorkspace)
    taskset.add(MountTmpFsWorkspace)
    taskset.add(UnmountTmpFsWorkspace)
    taskset.add(DeleteTmpFsWorkspace)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    counter_task(taskset, MountTmpFsWorkspace, UnmountTmpFsWorkspace)
    counter_task(taskset, CreateTmpFsWorkspace, DeleteTmpFsWorkspace)
