import tasks


def resolve_tasks(taskset, manifest):
	taskset.add(tasks.InstallCloudSDK)
	taskset.add(tasks.RemoveCloudSDKTarball)
