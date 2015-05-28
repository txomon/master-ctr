#!/usr/bin/python2
from __future__ import print_function
import sys
sys.path.append('/usr/realtime/rtai-py/')
import rtai
import ctypes
import time
import numpy as np
import matplotlib.pyplot as plt

class scope_data(ctypes.Structure):
	_fields_=[('time',ctypes.c_double),
	('value',ctypes.c_double)]


task = rtai.rt_task_init_schmod(rtai.nam2num("LAT2"),20,0,0,0,0XF)
plt.axis([0,1000,0,1])
plt.ion()
mbx_scope = rtai.rt_get_adr(rtai.nam2num("MBX3"))
print(mbx_scope)
scope=scope_data()

setpoint = ctypes.c_double()
setpoint_mbx = rtai.rt_mbx_init(rtai.nam2num("MBX4"),ctypes.sizeof(setpoint))
setpoint.value=1

while(True):
	rtai.rt_mbx_receive(mbx_scope, ctypes.byref(scope), ctypes.sizeof(scope))
	time = float(scope.time)
	value = float(scope.value)
	plt.scatter(time,value)
	plt.draw()
	rtai.rt_mbx_send_if(setpoint_mbx, ctypes.byref(setpoint), ctypes.sizeof(setpoint))
