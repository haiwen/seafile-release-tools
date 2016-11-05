#!/usr/bin/env python
#coding: UTF-8
"""
Android devs would publish seadroid apk in github release page. This script
is used to upload the apk to Bintray and Google Play.

Workflow:

- Fetch the latest apk (and changelog) from github release.
- Upload apk to bintray
- Upload apk to Google Play, and update the changelog

Still in progress.
"""

import argparse
import base64
import os
from os.path import abspath, basename, exists, dirname, join
import logging

from utils import setup_logging, download_apk_file
from utils.google_play import get_google_play_latest_release, google_play_upload
from utils.github import get_github_latest_release, get_github_version_info

logger = logging.getLogger(__file__)

DEFAULT_JSON_KEYFILE = join(dirname(abspath(__file__)), 'google-api-key.json')

def parse_args():
    argparser = argparse.ArgumentParser(add_help=False)
    argparser.add_argument(
        '--json-keyfile',
        help='The json file that contains the key to auth with google api',
        default=DEFAULT_JSON_KEYFILE,
    )
    argparser.add_argument(
        '--package-name',
        default='com.seafile.seadroid2',
        help='The package name of the apk.'
    )
    argparser.add_argument(
        '--local-publish',
        action='store_true',
        help='The package name of the apk.'
    )
    argparser.add_argument(
        '--version',
        help='Specify the version to publish to google play. If not set the latest github release would be used.'
    )
    return argparser.parse_args()

def should_publish(args):
    if 'TRAVIS' in os.environ:
        if 'TRAVIS_TAG' in os.environ:
            return True
        else:
            logger.info('skip publishing since current build is not triggered by a tag')
            return False
    else:
        if args.local_publish:
            return True
        else:
            logger.info('skip publishing since --local-publish is not set')
            return False

def main():
    args = parse_args()
    assert os.path.exists(args.json_keyfile)

    if args.version:
        version, version_code, changelog, apk_download_url = get_github_version_info(args.version)
    else:
        version, version_code, changelog, apk_download_url = get_github_latest_release()
        logger.info('latest version on github: %s', version)
        logger.info('latest version code on github: %s', version_code)

    google_play_version_code = get_google_play_latest_release(args.json_keyfile, args.package_name)
    logger.info('latest published version code on google play: %s', google_play_version_code)

    google_play_version_code = int(google_play_version_code)
    version_code = int(version_code)

    if google_play_version_code < version_code:
        if should_publish(args):
            logger.info('Publishing latest release to google play')
            apk_file = download_apk_file(apk_download_url)
            google_play_upload(apk_file, args.package_name, args.json_keyfile, changelog)
    else:
        logger.info('The version on google play is up to date.')

if __name__ == '__main__':
    setup_logging()
    logger.info('script started')
    if 'TRAVIS' in os.environ:
        logger.info('running on travis ci')
    else:
        logger.info('running on local machine')
    main()
