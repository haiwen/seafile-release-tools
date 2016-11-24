from __future__ import absolute_import
import os
import logging
import qiniu
from qiniu.services.storage.bucket import BucketManager

logger = logging.getLogger(__name__)

class QiniuClient(object):
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.q = qiniu.Auth(self.access_key, self.secret_key)
        self.bm = BucketManager(self.q)

    def upload_file(self, fn, bucket='seafile-downloads'):
        key = os.path.basename(fn)
        logging.info('uploading file %s to bucket %s', key, bucket)
        self._remove_existing_file(bucket, key)
        token = self.q.upload_token(bucket)
        ret, info = qiniu.put_file(token, key=key, file_path=fn)
        if ret is None:
            raise Exception('Error when uploading file %s to bucket %s: %s', key, bucket, info)

    def _remove_existing_file(self, bucket, key):
        ret = self.bm.stat(bucket, key)
        if ret[0] is None:
            return
        else:
            logger.warning('file %s already exists in bucket %s, deleting it', key, bucket)
            self.bm.delete(bucket, key)
            logger.warning('previous version of file %s deleted', key)

def qiniu_upload(access_key, secret_key, fn):
    QiniuClient(access_key, secret_key).upload_file(fn)
