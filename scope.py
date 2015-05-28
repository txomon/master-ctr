#!/usr/bin/env python
from __future__ import print_function
import sys

sys.path.append('/usr/realtime/rtai-py/')
import rtai
import ctypes
import time

import logging
from threading import Timer
from collections import deque

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

class scope_data_structure(ctypes.Structure):
    _fields_ = [
        ('time', ctypes.c_double),
        ('setpoint', ctypes.c_double),
        ('feedback', ctypes.c_double),
    ]

task = rtai.rt_task_init_schmod(rtai.nam2num("LAT2"), 20, 0, 0, 0, 0XF)

class RtaiScope(object):
    def __init__(self):
        self.connections = []
        self.scope_mbx = rtai.rt_get_adr(rtai.nam2num("MBX3"))
        self.scope = scope_data_structure()
        self.setpoint_mbx = rtai.rt_get_adr(rtai.nam2num("MBX4"))
        self.setpoint = ctypes.c_double()
	logger.debug("Setting up timer for rtai functionality")
        t = Timer(2, self.read_rtai)
        t.start()

    def new_connection(self, con):
        self.connections.append(con)

    def closed_connection(self, con):
        self.connections.remove(con)

    def handle_request(self, con, msg):
        logger.debug("Received: " + repr(msg))
        if msg['type'] == 'setpoint':
            self.rtai_setpoint(msg['message'])

    def rtai_setpoint(self, setpoint):
        if self.setpoint.value == setpoint:
            return
        self.setpoint.value = setpoint
        rtai.rt_mbx_send(self.setpoint_mbx, ctypes.byref(self.setpoint), ctypes.sizeof(self.setpoint))

    def read_rtai(self):
        while True:
            rtai.rt_mbx_receive(self.scope_mbx, ctypes.byref(self.scope), ctypes.sizeof(self.scope))
            time = float(self.scope.time)
            control = float(self.scope.control)
            feedback = float(self.scope.feedback)
            data = {
                "time": time,
                "control": control,
                "feedback": feedback,
            }
            logger.debug("RTAI reported: "+ repr(data))
            for con in self.connections:
                con.send('{"type": "data", "message":' + json.dumps(data) + '}')

app = RtaiScope()


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
    def index(self):
        handler = cherrypy.request.ws_handler


cherrypy.quickstart(Root(), '/', config={
    '/': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': WebSocketHandler,
    },
})

