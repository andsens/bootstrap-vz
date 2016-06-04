from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import image
from bootstrapvz.common.tools import log_check_call
import os


class CreateImageTarball(Task):
    description = 'Creating tarball with image'
    phase = phases.image_registration
    predecessors = [image.MoveImage]

    @classmethod
    def run(cls, info):
        image_name = info.manifest.name.format(**info.manifest_vars)
        filename = image_name + '.' + info.volume.extension

        tarball_name = image_name + '.tar.gz'
        tarball_path = os.path.join(info.manifest.bootstrapper['workspace'], tarball_name)
        info._oracle['tarball_path'] = tarball_path
        log_check_call(['tar', '--sparse', '-C', info.manifest.bootstrapper['workspace'],
                        '-caf', tarball_path, filename])


class UploadImageTarball(Task):
    description = 'Uploading image tarball'
    phase = phases.image_registration
    predecessors = [CreateImageTarball]

    @classmethod
    def run(cls, info):
        info._oracle['client'].file_path = info._oracle['tarball_path']
        info._oracle['client'].upload_file()


class DownloadImageTarball(Task):
    description = 'Downloading image tarball for integrity verification'
    phase = phases.image_registration
    predecessors = [UploadImageTarball]

    @classmethod
    def run(cls, info):
        tmp_tarball_path = '{tarball_path}-{pid}.tmp'.format(
            tarball_path=info._oracle['tarball_path'],
            pid=os.getpid(),
        )
        info._oracle['client'].target_file_path = tmp_tarball_path
        info._oracle['client'].download_file()


class CompareImageTarballs(Task):
    description = 'Comparing uploaded and downloaded image tarballs hashes'
    phase = phases.image_registration
    predecessors = [DownloadImageTarball]

    @classmethod
    def run(cls, info):
        info._oracle['client'].compare_files()
        os.remove(info._oracle['client'].target_file_path)
