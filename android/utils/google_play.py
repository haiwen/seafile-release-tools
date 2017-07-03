import httplib2
from apiclient.discovery import build  # pylint:disable=import-error
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

# The track of google play to publish to. Can be 'alpha', beta', 'production' or 'rollout'
TRACK = 'production'

def _get_service(json_keyfile=None):
    http = httplib2.Http()

    if json_keyfile:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            json_keyfile,
            scopes='https://www.googleapis.com/auth/androidpublisher')

        http = credentials.authorize(http)

    service = build('androidpublisher', 'v2', http=http)
    return service

def google_play_upload(apk_file, package_name, json_keyfile, changelog=''):
    service = _get_service(json_keyfile)

    try:
        edit_request = service.edits().insert(
            body={}, packageName=package_name)
        result = edit_request.execute()
        edit_id = result['id']

        apk_response = service.edits().apks().upload(
            editId=edit_id, packageName=package_name,
            media_body=apk_file).execute()

        print('Version code %d has been uploaded' % apk_response['versionCode'])

        track_response = service.edits().tracks().update(
            editId=edit_id,
            track=TRACK,
            packageName=package_name,
            body={u'versionCodes': [apk_response['versionCode']]}).execute()

        print('Track %s is set for version code(s) %s' % (
            track_response['track'], str(track_response['versionCodes'])))

        listing_response = service.edits().apklistings().update(
            editId=edit_id, packageName=package_name, language='en-US',
            apkVersionCode=apk_response['versionCode'],
            body={'recentChanges': changelog}).execute()

        print('Listing for language %s was updated.' % listing_response['language'])

        commit_request = service.edits().commit(
            editId=edit_id, packageName=package_name).execute()

        print('Edit "%s" has been committed' % (commit_request['id']))

    except client.AccessTokenRefreshError:
        print(
            'The credentials have been revoked or expired, please re-run the '
            'application to re-authorize')

def get_google_play_latest_release(json_keyfile, package_name='com.seafile.seadroid2'):
    """
    Returns the latest published version on google play.
    """
    service = _get_service(json_keyfile)
    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']

    apks_result = service.edits().apks().list(
        editId=edit_id, packageName=package_name).execute()

    version_code = apks_result['apks'][-1]['versionCode']
    return version_code


if __name__ == '__main__':
    pass
    # get_google_play_latest_release(*sys.argv[1:])
