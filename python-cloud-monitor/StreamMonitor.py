from time import sleep
import json
from WebsocketMonitor import WebsocketMonitor
import logging
import serial


logger = logging.getLogger(__name__)
last = None

class StreamMonitor():

    def parse_pkt(self, device_id, pkt):
        if pkt['type'] == 'connection_change':
            if pkt['state'] == 0:
                logger.info('Device %d offline', device_id)
            elif pkt['state'] == 1:
                logger.info('Device %d unstable', device_id)
            elif pkt['state'] == 2:
                logger.info('Device %d online', device_id)
            if self.ser is not None:
                self.ser.write('D%d,%d\r\n')
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
        if self.ser is not None:
            self.ser.write('C%d\r\n', connected)
        if connected:
            for device_id in self.device_ids:
                msg = '{"name":"subscribe", "args":{"device_id":"%s"}}' % device_id
                self.conn.ws.send(msg)

    def __init__(self, access_token, device_ids, port=None, baud=115200):
        if isinstance(device_ids, list):
            self.device_ids = device_ids
        else:
            self.device_ids = [device_ids]
        self.connected = False
        if port is not None:
            self.ser = serial.Serial(port, baud)
        else:
            self.ser = None
        self.msgcount = {}
        self.access_token = access_token
        self.conn = WebsocketMonitor(self.access_token,
                on_message=self.on_message, on_state_change=self.on_state_change)

    def connect(self):
        self.conn.connect()

    def disconnect(self):
        self.conn.disconnect()


logging.basicConfig(level=logging.INFO)
