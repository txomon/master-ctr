#!/usr/bin/python2
from __future__ import print_function
import sys

sys.path.append('/usr/realtime/rtai-py/')
import rtai
import ctypes
import time


class scope_data_structure(ctypes.Structure):
    _fields_ = [
        ('time', ctypes.c_double),
        ('setpoint', ctypes.c_double),
        ('feedback', ctypes.c_double),
    ]

task = rtai.rt_task_init_schmod(rtai.nam2num("LAT2"), 20, 0, 0, 0, 0XF)
mbx_scope = rtai.rt_get_adr(rtai.nam2num("MBX3"))
setpoint_mbx = rtai.rt_get_adr(rtai.nam2num("MBX4"))
setpoint = ctypes.c_double()
scope = scope_data_structure()

setpoint.value = 1

while (True):
    rtai.rt_mbx_receive(mbx_scope, ctypes.byref(scope), ctypes.sizeof(scope))
    time = float(scope.time)
    control = float(scope.control)
    feedback = float(scope.feedback)
