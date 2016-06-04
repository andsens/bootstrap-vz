import tasks
import os.path


def validate_manifest(data, validator, error):
    schema_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'manifest-schema.yml'))
    validator(data, schema_path)


def resolve_tasks(taskset, manifest):
    taskset.add(tasks.AddGoogleCloudRepoKey)
    if manifest.plugins['google_cloud_repo'].get('enable_keyring_repo', False):
        taskset.add(tasks.AddGoogleCloudRepoKeyringRepo)
        taskset.add(tasks.InstallGoogleCloudRepoKeyringPackage)
        if manifest.plugins['google_cloud_repo'].get('cleanup_bootstrap_key', False):
            taskset.add(tasks.CleanupBootstrapRepoKey)
