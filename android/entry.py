#!/usr/bin/env python
#coding: UTF-8

"""
Entry script for seafile android client package/release automation.

Workflow:

- When triggered by a tag like `android-pre-2.2.0`, it would build seadroid apk with seadroid 2.2.0 tag.
Then it would upload the signed apk to github pre release of seadroid projet.
The content in file changelog.md would be used as the releasae changelog.

- When triggered by a tag like `android-2.2.0`, it would mark the github pre-release as production release, and also upload the apk to google play.
"""

from __future__ import print_function

import argparse
import logging
import os
import re
import sys
from os.path import abspath, basename, dirname, exists, join

from android.builder import APKBuilder
from android.googleplay_uploader import GooglePlayUploader
from android.oss_uploader import OSSUploader
from android.releaser import GithubReleaser
from android.utils import read_file_content, setup_logging
from android.utils.slack_notify import send_slack_msg

logger = logging.getLogger(__name__)

PRE_RELEASE_PATTERN = re.compile('^android-([0-9.]+)-pre$')
PROD_RELEASE_PATTERN = re.compile('^android-([0-9.]+)$')

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='lins05/seadroid')
    ap.add_argument(
        '--package-name',
        default='com.seafile.seadroid2',
        help='The package name of the apk.'
    )

    return ap.parse_args()

def error_and_exit(msg, code=1):
    print('Error: ' + msg)
    sys.exit(code)

def read_android_changelog():
    # TODO: warn if changelog is not updated?
    fn = join(dirname(abspath(__file__)), 'changelog.md')
    return read_file_content(fn)

def notify_slack(msg):
    send_slack_msg(msg, botname='seadroid-travis-builder')

def main():
    args = parse_args()
    travis_tag = os.environ.get('TRAVIS_TAG', '')
    if not travis_tag:
        error_and_exit('Not triggered by a tag, skip buildding', 0)
    m = PRE_RELEASE_PATTERN.match(travis_tag)
    prerelease = False
    if m:
        seadroid_tag = m.group(1)
        prerelease = True
    else:
        m = PROD_RELEASE_PATTERN.match(travis_tag)
        if m:
            seadroid_tag = m.group(1)

    if not seadroid_tag:
        error_and_exit('unknown tag ' + travis_tag)

    releaser = GithubReleaser(args.repo)

    if prerelease:
        logger.info(f'going to build pre release {seadroid_tag}')
        builder = APKBuilder(seadroid_tag)
        changelog = read_android_changelog()

        builder.build()

        releaser.create_pre_release(seadroid_tag, changelog, builder.get_output())
        msg = f'Seadroid <https://github.com/{args.repo}/releases/tag/{seadroid_tag}|{seadroid_tag}> has been published to github'
        notify_slack(msg)
    else:
        logger.info(f'going to release {seadroid_tag} and upload it to google play')
        google_uploader = GooglePlayUploader()
        oss_uploader = OSSUploader()

        releaser.mark_as_prod(seadroid_tag)
        if google_uploader.upload(seadroid_tag, args.package_name):
            msg = f'Seadroid <https://github.com/{args.repo}/releases/tag/{seadroid_tag}|{seadroid_tag}> has been published to Google Play'
            notify_slack(msg)

        oss_uploader.upload_file(seadroid_tag)

if __name__ == '__main__':
    setup_logging()
    logger.info('script started')
    if 'TRAVIS' in os.environ:
        logger.info('running on travis ci')
    else:
        logger.info('running on local machine')
    main()
