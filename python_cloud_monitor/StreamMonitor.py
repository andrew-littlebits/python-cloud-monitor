from time import sleep
import json
from WebsocketMonitor import WebsocketMonitor
import logging
from slacker import Slacker
from time import time


logger = logging.getLogger(__name__)
last = None

class StreamMonitor():

    def parse_pkt(self, device_id, pkt):
        if pkt['type'] == 'connection_change':
            if pkt['state'] == 0:
                logger.info('Device %s offline', self.device_ids[device_id])
            elif pkt['state'] == 1:
                logger.info('Device %s unstable', self.device_ids[device_id])
            elif pkt['state'] == 2:
                logger.info('Device %s online', self.device_ids[device_id])
            # Do not report any messages recieved within first 2 seconds
            if self.slack is not None and (time() - self.connect_time) > 2.0:
                for user in self.slack_users:
                    if pkt['state'] == 0:
                        self.slack.chat.post_message(user,
                        '[%s] I just went offline' % self.device_ids[device_id],
                        self.slack_botname)
                    elif pkt['state'] == 1:
                        self.slack.chat.post_message(user,
                        '[%s] My connection is unstable' % self.device_ids[device_id],
                        self.slack_botname)
                    elif pkt['state'] == 2:
                        self.slack.chat.post_message(user,
                        '[%s] I came online' % self.device_ids[device_id],
                        self.slack_botname)
        else:
            if not device_id in self.msgcount:
                self.msgcount[device_id] = 1
            self.msgcount[device_id] += 1

    def on_message(self, message):
        pkt = json.loads(message)
        # Whyyy?
        while not isinstance(pkt, dict):
            pkt = json.loads(pkt)
        try:
            for i in range(len(self.device_ids)):
                device_id = self.device_ids[i]
                if pkt['from']['device']['id'] == device_id:
                    self.parse_pkt(i, pkt)
        except KeyError, TypeError:
            logger.error('Message malformed: %s', pkt)


    def on_state_change(self, connected):
        self.connected = connected
        logger.debug('State change: '+str(connected))
        if connected:
            for device_id in self.device_ids:
                msg = '{"name":"subscribe", "args":{"device_id":"%s"}}' % device_id
                self.conn.ws.send(msg)
        # Do not report any messages recieved within first 2 seconds
        if self.slack is not None and (time() - self.connect_time) > 2.0:
            for user in self.slack_users:
                if connected:
                    self.slack.chat.post_message(user,
                    'Regained connection to API server',
                    self.slack_botname)
                else:
                    self.slack.chat.post_message(user,
                    'Lost connection to API server',
                    self.slack_botname)

    def __init__(self, access_token, device_ids, slack_token=None,
            slack_users=None, slack_botname='StreamMonitor'):
        if isinstance(device_ids, list):
            self.device_ids = device_ids
        else:
            self.device_ids = [device_ids]
        if slack_token is not None:
            self.slack = Slacker(slack_token)
        else:
            self.slack = None
        if isinstance(slack_users, list):
            self.slack_users = slack_users
        elif slack_users is not None:
            self.slack_users = [slack_users]
        else:
            self.slack_users = []
        self.slack_botname = slack_botname
        self.connected = False
        self.connect_time = time()
        self.msgcount = {}
        self.access_token = access_token
        self.conn = WebsocketMonitor(self.access_token,
                on_message=self.on_message, on_state_change=self.on_state_change)

    def connect(self):
        self.connect_time = time()
        self.conn.connect()

    def disconnect(self):
        self.conn.disconnect()
