from __future__ import print_function, unicode_literals
import logging
from threading import Timer
from ws4py.client.threadedclient import WebSocketClient

try:
    import simplejson as json
except ImportError:
    import json

__author__ = 'javier'

logger = logging.getLogger()


class WSClient(WebSocketClient):
    def opened(self):
        logger.info("Connection to data server stabilised")

    def closed(self, code, reason=None):
        logger.info("Connection to data server closed")
        self.notify_closed(code, reason)

    def received_message(self, message):
        self.notify_data(message.data)


class Application(object):
    def __init__(self, server):
        self.connections = {}
        self.data_server = server
        self.data_server_closed()

    def data_server_closed(self, code=None, reason=None):
        t = Timer(5, self.create_client)
        t.start()
        logger.info('Retrying reconnection in 5 secs')

    def create_client(self):
        logger.info('Retrying reconnection...')
        self.client = WSClient(self.data_server)
        self.client.notify_closed = self.data_server_closed
        self.client.notify_data = self.handle_data
        try:
            self.client.connect()
        except Exception:
            logger.info("Could not stablish connection to server")
            self.data_server_closed()

    def handle_data(self, data):
        logger.debug('Received data ' + data)
        try:
            d = json.loads(data)
        except ValueError:
            logger.exception("Exception on json decoding")
            raise
        if d['type'] == 'scope':
            self.handle_scope(d['message'])

    def handle_scope(self, msg):
        graph_data = [{
                          'id': 'main',
                          'signals': [
                              {
                                  'id': 0,
                                  'data': [msg['time']],
                              },
                              {
                                  'id': 1,
                                  'data': [msg['setpoint']],
                              },
                              {
                                  'id': 2,
                                  'data': [msg['feedback']],
                              },
                          ],
                          'controls': [],
                      }]
        for con in self.connections:
            self.send('data', con, graph_data)

    def send_error(self, connection, content):
        self.send('error', connection, content)

    def send(self, type, connection, content):
        try:
            text = json.dumps(content)
        except Exception as e:
            logger.exception("JSON loading failed")
            connection.send('{"type": "' + type + '", "message": "' + repr(
                content) + '"}')
            return
        connection.send('{"type": "' + type + '", "message": ' + text + '}')

    def new_connection(self, con):
        self.connections[con] = {'status': 'uninit'}
        logger.debug("Adding new connection " + repr(con))

    def closed_connection(self, con):
        self.connections.pop(con)
        logger.debug("Removing closed connection " + repr(con))

    def handle_request(self, connection, message):
        logger.debug('Handling', message)
        if not message.get('type', False):
            self.send_error(connection, message)
        if message['type'] == 'initialize':
            self.handle_initialize(connection, message)

    def handle_initialize(self, con, msg):
        init_msg = {
            'displays': [
                {
                    'id': 'main',
                    'axis': [0, 10, 0, 1],
                    'signals': [
                        {
                            'id': 0,
                            'name': 'time',
                        },
                        {
                            'id': 1,
                            'name': 'setpoint',
                        },
                        {
                            'id': 2,
                            'name': 'feedback',
                        },
                    ],
                    'controls': [],
                },
            ],
        }
        self.send('initialize', con, init_msg)
