#!/usr/bin/env python

import argparse
import ConfigParser
from StreamMonitor import StreamMonitor
from sys import exit
from os.path import exists, expanduser
import logging
from time import sleep


logger = logging.getLogger(__name__)
DEFAULT_CFG_PATHS = [expanduser('~/.cloud_monitor_credentials.cfg'),
                     './cloud_monitor_credentials.cfg']

def parse_args():
    config = ConfigParser.SafeConfigParser()
    config.read(DEFAULT_CFG_PATHS)

    parser = argparse.ArgumentParser(description=\
        'Monitor cloud bits using streaming API and notify via Slack')
    parser.add_argument('--access_token', type=str, default=None,
        help='The littleBits access token for the bits to be monitored')
    parser.add_argument('--device_ids', nargs='+', type=str, default=[],
        help='One or more littleBits device IDs to monitor')
    parser.add_argument('--slack_token', type=str, default=None,
        help='A slack API token (see https://api.slack.com/web)')
    parser.add_argument('--slack_users', nargs='+', type=str, default=None,
        help='A list of slack usernames to notify privately\
              Each must begin with "@". Be careful to not specify a channel!')
    parser.add_argument('--slack_botname', type=str, default='CloudMonitorBot',
        help='The name used by the slack bot')
    parser.add_argument('--debug', action='store_true', default=False,
        help='Enable debug logging')

    try:
        if len(config.items("Defaults")) > 0:
            logger.info("Loaded settings from a config file: %s" % DEFAULT_CFG_PATHS)
        defaults = dict(config.items("Defaults"))
        if 'device_ids' in defaults and defaults['device_ids'].find(',') > 0:
            defaults['device_ids'] = defaults['device_ids'].split(',')
        if 'slack_users' in defaults and defaults['slack_users'].find(',') > 0:
            defaults['slack_users'] = defaults['slack_users'].split(',')
        parser.set_defaults(**defaults)
    except ConfigParser.NoSectionError:
        logger.warn("Unable to find 'Defaults' section in config file %s",
            DEFAULT_CFG_PATHS)

    args = parser.parse_args()

    if args.access_token is None:
        print "access token is required"
        exit(1)
    if args.device_ids is None:
        print "one or more device ids required"
        exit(1)
    return args

def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    mon = StreamMonitor(args.access_token, args.device_ids,
        slack_token=args.slack_token, slack_users=args.slack_users,
        slack_botname=args.slack_botname)
    mon.connect()
    while(mon.conn.running):
        sleep(1.0)

if __name__ == '__main__':
    exit(main())
