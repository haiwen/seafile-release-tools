import logging

from android.utils import download_apk_file
from android.utils.github import get_github_version_info
from android.utils.google_play import get_google_play_latest_release, google_play_upload
from android.utils.keys_utils import get_keyfile
from android.utils.slack_notify import send_slack_msg

logger = logging.getLogger(__file__)

def notify_slack(msg):
    send_slack_msg(msg, botname='android-travis-upload')

class GooglePlayUploader:
    def __init__(self):
        pass

    def upload(self, tag, package_name):
        version, version_code, changelog, apk_download_url = get_github_version_info(tag)
        logger.info('latest version code on github: %s', version_code)
        json_keyfile = get_keyfile('google-api-key.json')
        google_play_version_code = get_google_play_latest_release(json_keyfile, package_name)
        logger.info('latest published version code on google play: %s', google_play_version_code)

        google_play_version_code = int(google_play_version_code)
        version_code = int(version_code)

        apk_file = None

        if google_play_version_code < version_code:
            apk_file = download_apk_file(apk_download_url)
            logger.info('Publishing latest release to google play')
            google_play_upload(apk_file, package_name, json_keyfile, changelog)
            notify_slack(f'Seafile apk <https://github.com/haiwen/seadroid/releases/tag/{version}|{version} (version code {version_code})> '
                         + 'has been published to Google Play')
            return True
        else:
            logger.info('The version on google play is up to date.')
