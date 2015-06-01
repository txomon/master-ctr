#!/usr/bin/env python
from __future__ import print_function
import logging
import threading
from collections import deque
import subprocess
import time
import fcntl
import os
import sys

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket

try:
    import simplejson as json
except ImportError:
    import json

cherrypy.config.update({'server.socket_port': 9001})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG)
logger = logging.getLogger()


class Server(object):
    def __init__(self):
        self.connections = []
        self.scope = subprocess.Popen(['./scope.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) 
        threading.Timer(0,self.send_data).start()

    def new_connection(self, con):
        self.connections.append(con)

    def closed_connection(self, con):
        self.connections.remove(con)

    def handle_request(self, con, msg):
        logger.log("Received: " + repr(msg))

    def send_data(self):
        time.sleep(1)
        fd = self.scope.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        while threading.active_count() > 3:
            if self.connections:
                try:
                    data = self.scope.stdout.readline()
                except: continue
                for con in self.connections:
                    con.send(data)
        self.scope.kill()
        self.scope.terminate()


app = Server()


class WebSocketHandler(WebSocket):
    def opened(self):
        app.new_connection(self)
        print('WS connection opened from', self.peer_address)

    def closed(self, code, reason=None):
        app.closed_connection(self)
        print('WS connection closed with code', code, reason)

    def received_message(self, message):
        try:
            request = json.loads(message.data)
        except ValueError as e:
            logger.exception("JSON not correctly formatted")
            return
        except Exception as e:
            logger.exception('JSON decode failed for message')
            return
        app.handle_request(self, request)

    def send(self, payload, binary=False):
        if self.terminated:
            return
        logger.debug("Sending: " + str(payload))
        super(WebSocketHandler, self).send(payload, binary)


class Root(object):
    @cherrypy.expose
    def index(self):
        handler = cherrypy.request.ws_handler


cherrypy.quickstart(Root(), '/', config={
    '/': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': WebSocketHandler,
    },
})
