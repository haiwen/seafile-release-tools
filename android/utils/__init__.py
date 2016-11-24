import logging
import os
import shutil
import sys
import tempfile

import requests

logger = logging.getLogger(__file__)

def setup_logging(level=logging.INFO):
    kw = {
        'format': '[%(asctime)s][%(name)s][%(levelname)s]: %(message)s',
        # 'format': '[%(asctime)s][%(module)s]: %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': level,
        'stream': sys.stdout
    }

    logging.basicConfig(**kw)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(
        logging.WARNING)
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)
    logging.getLogger('oauth2client').setLevel(logging.WARNING)

def download_apk_file(url):
    """
    Download the url to a temporary path
    :type url: str
    """
    # url is like https://github.com/haiwen/seadroid/releases/download/2.1.6/seafile-2.1.6.apk
    resp = requests.get(url, stream=True)
    path = os.path.join(tempfile.gettempdir(), os.path.basename(url))
    logger.info('downloading %s to %s', url, path)
    with open(path, 'wb') as f:
        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, f)
    logger.info('downloaded file %s', path)
    return path
