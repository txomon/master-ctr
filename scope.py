from __future__ import print_function
import rtai
import ctypes
import time
import numpy as np
import matplotlib.pyplot as plt


task = rtai.rt_task_init_schmod(rtai.nam2num("LAT2"),20,0,0,0,0XF)

plt.axis([0,1000,0,1])
plt.ion()
i=0


mbx_scope = rtai.rt_get_adr(rtai.nam2num("MBX3"))

print(mbx_scope)
scope=ctypes.c_double()

while(True):
	i=i+0.005
	print("checkpoint")
	rtai.rt_mbx_receive(mbx_scope, ctypes.byref(scope), ctypes.sizeof(scope))
        print("checkpoint2")
	value = float(scope.value)
	plt.scatter(i,value)
	plt.draw()

 

