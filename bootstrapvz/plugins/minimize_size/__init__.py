import tasks.mounts
import tasks.shrink
import tasks.apt
import tasks.dpkg
from bootstrapvz.common.tasks import locale


def validate_manifest(data, validator, error):
    from bootstrapvz.common.tools import rel_path
    validator(data, rel_path(__file__, 'manifest-schema.yml'))

    if data['plugins']['minimize_size'].get('shrink', False) and data['volume']['backing'] != 'vmdk':
        error('Can only shrink vmdk images', ['plugins', 'minimize_size', 'shrink'])


def resolve_tasks(taskset, manifest):
    taskset.update([tasks.mounts.AddFolderMounts,
                    tasks.mounts.RemoveFolderMounts,
                    ])
    if manifest.plugins['minimize_size'].get('zerofree', False):
        taskset.add(tasks.shrink.AddRequiredCommands)
        taskset.add(tasks.shrink.Zerofree)
    if manifest.plugins['minimize_size'].get('shrink', False):
        taskset.add(tasks.shrink.AddRequiredCommands)
        taskset.add(tasks.shrink.ShrinkVolume)
    if 'apt' in manifest.plugins['minimize_size']:
        apt = manifest.plugins['minimize_size']['apt']
        if apt.get('autoclean', False):
            taskset.add(tasks.apt.AutomateAptClean)
        if 'languages' in apt:
            taskset.add(tasks.apt.FilterTranslationFiles)
        if apt.get('gzip_indexes', False):
            taskset.add(tasks.apt.AptGzipIndexes)
        if apt.get('autoremove_suggests', False):
            taskset.add(tasks.apt.AptAutoremoveSuggests)
        filter_tasks = [tasks.dpkg.CreateDpkgCfg,
                        tasks.dpkg.InitializeBootstrapFilterList,
                        tasks.dpkg.CreateBootstrapFilterScripts,
                        tasks.dpkg.DeleteBootstrapFilterScripts,
                        ]
    if 'dpkg' in manifest.plugins['minimize_size']:
        dpkg = manifest.plugins['minimize_size']['dpkg']
        if 'locales' in dpkg:
            taskset.update(filter_tasks)
            taskset.add(tasks.dpkg.FilterLocales)
            # If no locales are selected, we don't need the locale package
            if len(dpkg['locales']) == 0:
                taskset.discard(locale.LocaleBootstrapPackage)
                taskset.discard(locale.GenerateLocale)
        if dpkg.get('exclude_docs', False):
            taskset.update(filter_tasks)
            taskset.add(tasks.dpkg.ExcludeDocs)


def resolve_rollback_tasks(taskset, manifest, completed, counter_task):
    counter_task(taskset, tasks.mounts.AddFolderMounts, tasks.mounts.RemoveFolderMounts)
    counter_task(taskset, tasks.dpkg.CreateBootstrapFilterScripts, tasks.dpkg.DeleteBootstrapFilterScripts)
