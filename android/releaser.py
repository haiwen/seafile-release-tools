"""
See https://developer.github.com/v3/repos/releases/ for the specs of github release api.
"""

import json
import logging
import urllib
from os.path import abspath, basename, dirname, exists, join

import requests

from android.utils.keys_utils import read_key_file
from android.utils.rest import RestClient

logger = logging.getLogger(__file__)

class GithubApi(RestClient):
    def __init__(self, user, token, repo):
        super(GithubApi, self).__init__('https://api.github.com', auth=(user, token))
        self.repo = repo

    def get_release(self, tag, repo=None):
        repo = repo or self.repo

        resp = self.get(f'/repos/{repo}/releases/tags/{tag}')
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return None
        else:
            raise RuntimeError(f'failed to get release {tag}: {resp.status_code} {resp.content}')

    def create_release(self, tag, changelog, prerelease=True, repo=None):
        repo = repo or self.repo

        release_name = f'Seafile-{tag}'
        data = {
            'name': release_name,
            'tag_name': tag,
            'body': changelog,
            'prerelease': prerelease,
            'draft': False
        }

        release = self.get_release(tag, repo)

        if release:
            release_id = release['id']
            if any([release[k] != data[k] for k in data]):
                logger.info('release %s already exists, pathching it', release_name)
                resp = self.patch(f'/repos/{repo}/releases/{release_id}', data=data)
                resp.raise_for_status()
            else:
                logger.info('release %s already exists, no need to create', release_name)
            return release_id, release['upload_url']
        else:
            logger.info('creating new prerelease %s', release_name)
            resp = self.post(f'/repos/{repo}/releases', data=data)
            resp.raise_for_status()
            j = resp.json()
            return j['id'], j['upload_url']

    def remove_release_file_if_exists(self, release_id, fn, repo=None):
        repo = repo or self.repo
        resp = self.get(f'/repos/{repo}/releases/{release_id}/assets')
        resp.raise_for_status()

        asset_id = None
        for entry in resp.json():
            if entry['name'] == fn:
                asset_id = entry['id']

        if asset_id:
            resp = self.delete(f'/repos/{repo}/releases/assets/{asset_id}')
            resp.raise_for_status()
            logger.info(f'delete existing asset {fn} before uploading the new version')
        else:
            logger.debug(f'No existing asset {fn}')

    def upload_release_file(self, release_id, fn, repo=None):
        repo = repo or self.repo

        self.remove_release_file_if_exists(release_id, basename(fn))

        with open(fn, 'rb') as fp:
            headers = self.headers.copy()
            headers['Content-Type'] = 'application/zip'
            name = urllib.parse.quote(basename(fn))
            resp = self.post(f'https://uploads.github.com/repos/{repo}/releases/{release_id}/assets?name={name}',
                             data=fp,
                             headers=headers)
            resp.raise_for_status()

    def mark_as_prod(self, tag, repo=None):
        repo = repo or self.repo

        release = self.get_release(tag, repo)
        if not release:
            raise RuntimeError(f'No such release matching tag {tag}')

        if release['prerelease'] or release['draft']:
            logger.info('changing %s from prerelease to prod release', tag)
            release_id = release['id']
            data = {
                'prerelease': False,
                'draft': False,
            }
            resp = self.patch(f'/repos/{repo}/releases/{release_id}', data=data)
            resp.raise_for_status()
        else:
            logger.info('%s is already a prod release', tag)

class GithubReleaser:
    def __init__(self, repo):
        self.github_client = None
        self.repo = repo
        self.init_github_client()

    def init_github_client(self):
        d = json.loads(read_key_file('ci.json'))
        user = d['username']
        token = d['token']
        self.github_client = GithubApi(user, token, repo=self.repo)
        logger.info('inititialized github client')

    def create_pre_release(self, tag, changelog, apkfile):
        logger.info('creating github prerelease %s', tag)
        release_id, _ = self.github_client.create_release(tag, changelog)
        logger.info('prerelease %s created', tag)

        logger.info('uploading asset %s to release', basename(apkfile))
        self.github_client.upload_release_file(release_id, apkfile)
        logger.info('file %s uploaded', basename(apkfile))

    def mark_as_prod(self, tag):
        self.github_client.mark_as_prod(tag)
