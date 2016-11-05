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

from apiclient.discovery import build # pylint:disable=import-error
import httplib2
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

# The track of google play to publish to. Can be 'alpha', beta', 'production' or 'rollout'
TRACK = 'alpha'

def parse_args():
    argparser = argparse.ArgumentParser(add_help=False)
    argparser.add_argument(
        '--json-keyfile',
        help='The json file that contains the key to auth with google api'
    )
    argparser.add_argument(
        'package_name',
        nargs='?',
        default='com.seafile.seadroid2',
        help='The package name of the apk.'
    )
    argparser.add_argument(
        'apk_file',
        nargs='?',
        default='/data/downloads/hello-world-1.2.apk',
        help='The path to the APK file to upload.'
    )
    args = argparser.parse_args()
    if not args.json_keyfile:
        json_from_environ = 
        if not os.environment
        args.json_keyfile = 

def main():
    args = parse_args()

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        args.json_keyfile
        scopes='https://www.googleapis.com/auth/androidpublisher')

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build('androidpublisher', 'v2', http=http)

    package_name = args.package_name
    apk_file = args.apk_file

    try:
        edit_request = service.edits().insert(
            body={}, packageName=package_name)
        result = edit_request.execute()
        edit_id = result['id']

        apk_response = service.edits().apks().upload(
            editId=edit_id, packageName=package_name,
            media_body=apk_file).execute()

        print 'Version code %d has been uploaded' % apk_response['versionCode']

        track_response = service.edits().tracks().update(
            editId=edit_id,
            track=TRACK,
            packageName=package_name,
            body={u'versionCodes': [apk_response['versionCode']]}).execute()

        print 'Track %s is set for version code(s) %s' % (
            track_response['track'], str(track_response['versionCodes']))

        listing_response = service.edits().apklistings().update(
            editId=edit_id, packageName=package_name, language='en-US',
            apkVersionCode=apk_response['versionCode'],
            body={'recentChanges': 'Apk recent changes in en-US'}).execute()

        print 'Listing for language %s was updated.' % listing_response['language']

        commit_request = service.edits().commit(
            editId=edit_id, packageName=package_name).execute()

        print 'Edit "%s" has been committed' % (commit_request['id'])

    except client.AccessTokenRefreshError:
        print(
            'The credentials have been revoked or expired, please re-run the '
            'application to re-authorize')


if __name__ == '__main__':
    main()
