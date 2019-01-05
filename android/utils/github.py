from __future__ import print_function
import logging
import re
import time
import requests
from android.utils import setup_logging, http_get

def _get_version_code(tag):
    """
    Get the android app version code from AndroidManifest.xml"
    """
    url = 'https://raw.githubusercontent.com/haiwen/seadroid/{}/app/build.gradle'.format(tag)
    content = http_get(url).text
    # versionCode 74
    pattern = re.compile(r'versionCode (\d+)')
    for line in content.splitlines():
        m = re.search(pattern, line)
        if m:
            return m.group(1)

    raise RuntimeError('Failed to parse the versionCode from AndroidManifest.xml for tag {}'.format(tag))

def get_github_version_info(version=None):
    """
    Returns a four tuple of (version, version_code, changelog, download_url)
    """
    resp = http_get('https://api.github.com/repos/haiwen/seadroid/releases')
    releases = resp.json()
    print('releases json:', releases)
    if not version:
        ret = releases[0]
    else:
        for r in releases:
            if r['tag_name'] == version:
                ret = r
                break
        else:
            raise RuntimeError('No such release version {} for seadroid'.format(version))

    version_code = _get_version_code(ret['tag_name'])

    return ret['tag_name'], version_code, ret['body'], ret['assets'][0]['browser_download_url']

if __name__ == '__main__':
    setup_logging()
    print(get_github_version_info())
