#!/usr/bin/python2
from __future__ import print_function
import sys
sys.path.append('/usr/realtime/rtai-py/')
import rtai
import ctypes

class scope_data(ctypes.Structure):
	_fields_=[('time',ctypes.c_double),
	('value',ctypes.c_double)]


task = rtai.rt_task_init_schmod(rtai.nam2num("LAT1"),20,0,0,0,0XF)
rtai.rt_make_soft_real_time()
control_reference = rtai.rt_get_adr(rtai.nam2num("MBX1"))
plant_output = rtai.rt_get_adr(rtai.nam2num("MBX2"))

salida = scope_data()
scope_mbx = rtai.rt_mbx_init(rtai.nam2num("MBX3"),ctypes.sizeof(salida))
print(scope_mbx)
dato = ctypes.c_double()
data = ctypes.c_double()
e1=0
e2=0
w1=0
w2=0
i=0

while(True):
        i=i+0.005
	rtai.rt_mbx_receive(control_reference, ctypes.byref(data), ctypes.sizeof(data))
	e = float(data.value)
        w = 1.941*w1-0.9418*w2+2.451*0.000001*e1+2.402*0.000001*e2
	dato.value=w
	salida.value = w
	salida.time = i
	e1=e
	e2=e1
	w1=w
	w2=w1
	rtai.rt_mbx_send_if(plant_output, ctypes.byref(dato), ctypes.sizeof(dato))
	rtai.rt_mbx_send_if(scope_mbx, ctypes.byref(salida), ctypes.sizeof(salida))
        



