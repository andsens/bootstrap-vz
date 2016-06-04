from bootstrapvz.base import Task
from bootstrapvz.common import phases
from bootstrapvz.common.tasks import image
from bootstrapvz.common.tools import log_check_call
import os.path


class CreateTarball(Task):
    description = 'Creating tarball with image'
    phase = phases.image_registration
    predecessors = [image.MoveImage]

    @classmethod
    def run(cls, info):
        image_name = info.manifest.name.format(**info.manifest_vars)
        filename = image_name + '.' + info.volume.extension
        # ensure that we do not use disallowed characters in image name
        image_name = image_name.lower()
        image_name = image_name.replace(".", "-")
        info._gce['image_name'] = image_name
        tarball_name = image_name + '.tar.gz'
        tarball_path = os.path.join(info.manifest.bootstrapper['workspace'], tarball_name)
        info._gce['tarball_name'] = tarball_name
        info._gce['tarball_path'] = tarball_path
        # GCE requires that the file in the tar be named disk.raw, hence the transform
        log_check_call(['tar', '--sparse', '-C', info.manifest.bootstrapper['workspace'],
                        '-caf', tarball_path,
                        '--transform=s|.*|disk.raw|',
                        filename])


class UploadImage(Task):
    description = 'Uploading image to GCS'
    phase = phases.image_registration
    predecessors = [CreateTarball]

    @classmethod
    def run(cls, info):
        log_check_call(['gsutil', 'cp', info._gce['tarball_path'],
                        info.manifest.provider['gcs_destination'] + info._gce['tarball_name']])


class RegisterImage(Task):
    description = 'Registering image with GCE'
    phase = phases.image_registration
    predecessors = [UploadImage]

    @classmethod
    def run(cls, info):
        image_description = info._gce['lsb_description']
        if 'description' in info.manifest.provider:
            image_description = info.manifest.provider['description']
            image_description = image_description.format(**info.manifest_vars)
        log_check_call(['gcloud', 'compute', '--project=' + info.manifest.provider['gce_project'],
                        'images', 'create', info._gce['image_name'],
                        '--source-uri=' + info.manifest.provider['gcs_destination'] + info._gce['tarball_name'],
                        '--description=' + image_description])
