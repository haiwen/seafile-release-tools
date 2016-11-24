#!/usr/bin/env python
#coding: UTF-8

import json
import sys
import os

import requests

def send_slack_msg(message, channel=None, at_users='', botname='slackbot', color='good'):
    """Send an audit log to Slack

    color can be "good", "warning", "danger" or any hex color code (#AABBCC)
    """
    url = os.environ.get('SLACK_NOTIFY_URL', '')
    if not url:
        raise RuntimeError('SLACK_NOTIFY_URL not set')
    channel = channel or os.environ.get('SLACK_NOTIFY_CHANNEL', '')
    if not channel:
        raise RuntimeError('SLACK_NOTIFY_CHANNEL not set')

    at_users = at_users or os.environ.get('SLACK_NOTIFY_USERS', '')
    if not at_users:
        raise RuntimeError('SLACK_NOTIFY_USERS not set')

    headers = {'Content-Type': 'application/json'}
    msg = ''
    if isinstance(at_users, basestring):
        at_users = at_users.split(',')
    for u in at_users:
        msg += "<@{}> ".format(u)
    msg += message

    params = {
        'username': botname,
        'icon_emoji': ':chicken:',
        'channel': '#' + channel.strip('#'),
        'attachments': [
            {'text': msg,
             'color': color},
        ],
    }
    r = requests.post(url, data=json.dumps(params), headers=headers)
    r.raise_for_status()

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--botname', default='slackbot')
    ap.add_argument('--at', default='')
    ap.add_argument('--color', default='good', choices=('good', 'bad'))
    ap.add_argument('channel')
    ap.add_argument('msg')

    args = ap.parse_args()

    assert all([' ' not in s for s in (args.channel, args.botname, args.at)])

    send_slack_msg(args.msg, args.channel, at_users=args.at.split(',') if args.at else [], botname=args.botname, color=args.color)

if __name__ == '__main__':
    main()
