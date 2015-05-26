#!/usr/bin/python2
from __future__ import print_function
import sys

sys.path.append('/usr/realtime/rtai-py/')
import rtai
import ctypes
import time


class scope_data(ctypes.Structure):
    _fields_ = [
        ('time', ctypes.c_double),
        ('control', ctypes.c_double),
        ('feedback', ctypes.c_double),
    ]


task = rtai.rt_task_init_schmod(rtai.nam2num("LAT2"), 20, 0, 0, 0, 0XF)
mbx_scope = rtai.rt_get_adr(rtai.nam2num("MBX3"))
scope = scope_data()

while (True):
    rtai.rt_mbx_receive(mbx_scope, ctypes.byref(scope), ctypes.sizeof(scope))
    time = float(scope.time)
    value = float(scope.value)
    print(time, value)
    plt.scatter(time, value)
    plt.draw()

 

