#!/usr/bin/env python
from __future__ import print_function
import logging
from os.path import abspath

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket

from application import Application


try:
    import simplejson as json
except ImportError:
    import json

cherrypy.config.update({'server.socket_port': 9000, 'server.socket_host': '0.0.0.0'})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG)
logger = logging.getLogger()

app = Application('ws://127.0.0.1:9001/')


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
        logger.debug("Answer: " + str(payload))
        super(WebSocketHandler, self).send(payload, binary)


class Root(object):
    @cherrypy.expose
    def ws(self):
        handler = cherrypy.request.ws_handler


cherrypy.quickstart(Root(), '/', config={
    '/ws': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': WebSocketHandler,
    },
    '/': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': abspath('./data'),
        'tools.staticdir.index': 'index.html',
    },
})
