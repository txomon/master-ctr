from __future__ import print_function
import rtai
import ctypes


task = rtai.rt_task_init_schmod(rtai.nam2num("LAT1"),20,0,0,0,0XF)
rtai.rt_make_soft_real_time()
mbx = rtai.rt_get_adr(rtai.nam2num("MBX1"))
mbx1 = rtai.rt_get_adr(rtai.nam2num("MBX2"))
print(mbx1)

salida=ctypes.c_double()
scope_mbx = rtai.rt_mbx_init(rtai.nam2num("MBX3"),ctypes.sizeof(salida))
print(scope_mbx)
dato=ctypes.c_double()
data = ctypes.c_double()
u1=0
u2=0
y1=0
y2=0

while(True):
	rtai.rt_mbx_receive(mbx, ctypes.byref(data), ctypes.sizeof(data))
	u = float(data.value)
        y = 1.941*y1-0.9418*y2+2.451*0.000001*u1+2.402*0.000001*u2
	dato.value=y
	salida.value = y
	u1=u
	u2=u1
	y1=y
	y2=y1
	rtai.rt_mbx_send(mbx1, ctypes.byref(dato), ctypes.sizeof(dato))
	rtai.rt_mbx_send_if(scope_mbx, ctypes.byref(salida), ctypes.sizeof(salida))




