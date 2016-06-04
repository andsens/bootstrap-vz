import hashlib
import logging
import os
import requests
from bootstrapvz.common.bytes import Bytes


class OracleStorageAPIClient:
    def __init__(self, username, password, identity_domain, container):
        self.username = username
        self.password = password
        self.identity_domain = identity_domain
        self.container = container
        self.base_url = 'https://' + identity_domain + '.storage.oraclecloud.com'
        self.log = logging.getLogger(__name__)

        # Avoid 'requests' INFO/DEBUG log messages
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

    def _fail(self, error):
        raise RuntimeError('Oracle Storage Cloud API - ' + error)

    @property
    def auth_token(self):
        headers = {
            'X-Storage-User': 'Storage-{id_domain}:{user}'.format(
                id_domain=self.identity_domain,
                user=self.username,
            ),
            'X-Storage-Pass': self.password,
        }
        url = self.base_url + '/auth/v1.0'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.headers.get('x-auth-token')
        else:
            self._fail(response.text)

    @property
    def chunk_size(self):
        file_size = os.path.getsize(self.file_path)
        if file_size > int(Bytes('300MiB')):
            chunk_size = int(Bytes('100MiB'))
        else:
            chunk_size = int(Bytes('50MiB'))
        return chunk_size

    def compare_files(self):
        uploaded_file_md5 = hashlib.md5()
        downloaded_file_md5 = hashlib.md5()
        files = [self.file_path, self.target_file_path]
        hashes = [uploaded_file_md5, downloaded_file_md5]
        for f, h in zip(files, hashes):
            with open(f, 'rb') as current_file:
                while True:
                    data = current_file.read(int(Bytes('8MiB')))
                    if not data:
                        break
                    h.update(data)
        if uploaded_file_md5.hexdigest() != downloaded_file_md5.hexdigest():
            self.log.error('File hashes mismatch')
        else:
            self.log.debug('Both files have the same hash')

    def create_manifest(self):
        headers = {
            'X-Auth-Token': self.auth_token,
            'X-Object-Manifest': '{container}/{object_name}-'.format(
                container=self.container,
                object_name=self.file_name,
            ),
            'Content-Length': '0',
        }
        url = self.object_url
        self.log.debug('Creating remote manifest to join chunks')
        response = requests.put(url, headers=headers)
        if response.status_code != 201:
            self._fail(response.text)

    def download_file(self):
        headers = {
            'X-Auth-Token': self.auth_token,
        }
        url = self.object_url
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code != 200:
            self._fail(response.text)
        with open(self.target_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=int(Bytes('8MiB'))):
                if chunk:
                    f.write(chunk)

    @property
    def file_name(self):
        return os.path.basename(self.file_path)

    @property
    def object_url(self):
        url = '{base}/v1/Storage-{id_domain}/{container}/{object_name}'.format(
            base=self.base_url,
            id_domain=self.identity_domain,
            container=self.container,
            object_name=self.file_name,
        )
        return url

    def upload_file(self):
        f = open(self.file_path, 'rb')
        n = 1
        while True:
            chunk = f.read(self.chunk_size)
            if not chunk:
                break
            chunk_name = '{name}-{number}'.format(
                name=self.file_name,
                number='{0:04d}'.format(n),
            )
            headers = {
                'X-Auth-Token': self.auth_token,
            }
            url = '{base}/v1/Storage-{id_domain}/{container}/{object_chunk_name}'.format(
                base=self.base_url,
                id_domain=self.identity_domain,
                container=self.container,
                object_chunk_name=chunk_name,
            )
            self.log.debug('Uploading chunk ' + chunk_name)
            response = requests.put(url, data=chunk, headers=headers)
            if response.status_code != 201:
                self._fail(response.text)
            n += 1
        self.create_manifest()
