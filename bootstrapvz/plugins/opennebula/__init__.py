

def resolve_tasks(taskset, manifest):
    import tasks
    from bootstrapvz.common.tasks import apt
    from bootstrapvz.common.releases import wheezy
    if manifest.release == wheezy:
        taskset.add(apt.AddBackports)
    taskset.update([tasks.AddONEContextPackage])
