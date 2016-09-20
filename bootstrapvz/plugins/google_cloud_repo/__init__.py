import tasks
from bootstrapvz.common.tools import rel_path


def validate_manifest(data, validator, error):
    validator(data, rel_path(__file__, 'manifest-schema.yml'))


def resolve_tasks(taskset, manifest):
    taskset.add(tasks.AddGoogleCloudRepoKey)
    if manifest.plugins['google_cloud_repo'].get('enable_keyring_repo', False):
        taskset.add(tasks.AddGoogleCloudRepoKeyringRepo)
        taskset.add(tasks.InstallGoogleCloudRepoKeyringPackage)
        if manifest.plugins['google_cloud_repo'].get('cleanup_bootstrap_key', False):
            taskset.add(tasks.CleanupBootstrapRepoKey)
