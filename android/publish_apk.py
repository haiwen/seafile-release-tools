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

from utils.google_play import google_play_upload

# The track of google play to publish to. Can be 'alpha', beta', 'production' or 'rollout'
TRACK = 'alpha'

def parse_args():
    argparser = argparse.ArgumentParser(add_help=False)
    argparser.add_argument(
        '--json-keyfile',
        help='The json file that contains the key to auth with google api',
        required=True,
    )
    argparser.add_argument(
        'package_name',
        default='com.seafile.seadroid2',
        help='The package name of the apk.'
    )
    argparser.add_argument(
        'apk_file',
        default='/data/downloads/hello-world-1.2.apk',
        help='The path to the APK file to upload.'
    )
    return argparser.parse_args()

def main():
    args = parse_args()

    google_play_upload(args.apk_file, args.package_name, args.json_keyfile)


if __name__ == '__main__':
    main()
