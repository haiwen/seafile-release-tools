import logging
import os

from android.utils import download_apk_file
from android.utils.github import get_github_version_info
from oss2 import Auth, Bucket

logger = logging.getLogger(__name__)

class OSSUploader(object):
    def __init__(self):
        access_key_id = os.environ['OSS_ACCESS_KEY_ID']
        access_key_secret = os.environ['OSS_ACCESS_KEY_SECRET']

        self.endpoint = os.environ.get('OSS_ENDPOINT', 'http://oss-cn-shanghai.aliyuncs.com')
        self.auth = Auth(access_key_id, access_key_secret)
        self.bucket_name = os.environ.get('OSS_BUCKET', 'seafile-downloads')
        self.bucket = Bucket(self.auth, self.endpoint, self.bucket_name)

    def upload_file(self, tag):
        _, _, _, apk_download_url = get_github_version_info(tag)
        apk_file = download_apk_file(apk_download_url)

        fn = os.path.basename(apk_file)
        logger.info('uploading file %s to bucket %s', fn, self.bucket_name)
        self._remove_existing_file(fn)
        with open(apk_file, 'rb') as f:
            self.bucket.put_object(fn, f)

    def _remove_existing_file(self, fn):
        if self.bucket.object_exists(fn):
            logger.warning('file %s already exists in bucket %s, deleting it', fn, self.bucket_name)
            self.bucket.delete_object(fn)
            logger.warning('previous version of file %s deleted', fn)
