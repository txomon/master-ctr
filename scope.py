#!/usr/bin/env python
from __future__ import print_function
import sys
import select

sys.path.append('/usr/realtime/rtai-py/')
import rtai
import ctypes
import time
import logging

try:
    import simplejson as json
except ImportError:
    import json

logging.basicConfig(format=logging.BASIC_FORMAT, level=logging.DEBUG)
logger = logging.getLogger()

class scope_data_structure(ctypes.Structure):
    _fields_ = [
        ('time', ctypes.c_double),
        ('setpoint', ctypes.c_double),
        ('feedback', ctypes.c_double),
    ]


class RtaiScope(object):
    def __init__(self):
        task = rtai.rt_task_init_schmod(rtai.nam2num("LAT2"), 20, 0, 0, 0, 0XF)
        self.scope_mbx = rtai.rt_get_adr(rtai.nam2num("MBX3"))
        self.scope = scope_data_structure()
        self.setpoint_mbx = rtai.rt_get_adr(rtai.nam2num("MBX4"))
        self.setpoint = ctypes.c_double()
	self.counter = 0

    def rtai_setpoint(self, setpoint):
        if self.setpoint.value == setpoint:
            return
        logger.debug('Changing setpoint')
        self.setpoint.value = setpoint
        rtai.rt_mbx_send(self.setpoint_mbx, ctypes.byref(self.setpoint), ctypes.sizeof(self.setpoint))

    def read_rtai(self):
        rtai.rt_mbx_receive(self.scope_mbx, ctypes.byref(self.scope), ctypes.sizeof(self.scope))
        time = float(self.scope.time)
        setpoint = float(self.scope.setpoint)
	self.setpoint.value = setpoint
        feedback = float(self.scope.feedback)
        data = {
            "time": time,
            "setpoint": setpoint,
            "feedback": feedback,
        }
	self.counter +=1
	if not self.counter % 100:
            print('{"type": "scope", "message":' + json.dumps(data) + '}')

class StreamingInput(object):
    def __init__(self):
        self.poller = select.poll()
        self.poller.register(sys.stdin, select.POLLIN)

    def poll(self):
        poll_res = self.poller.poll(0)
        if not poll_res:
            return False
        logger.debug("Received: "+ repr(poll_res))
        return poll_res[0][1]

    def read(self):
        poll = self.poll()
        if poll == 1:
            return sys.stdin.readline()
        elif poll > 4:
            raise ValueError()
        return None

if __name__ == '__main__':
    app = RtaiScope()
    stdin = StreamingInput()
    while True:
        app.read_rtai()
	try:
            line = stdin.read()
        except ValueError:
            sys.exit(0)
        if not line:
            continue

        msg = json.dumps(line.strip())
	if type(msg) in [str, unicode]:
            logger.debug("Input string: " + repr(msg))
            msg = {'type': 'setpoint', 'message': float(line)}
        else:
            logger.debug('Input json')
        app.rtai_setpoint(msg['message'])
