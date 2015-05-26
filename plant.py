#!/usr/bin/python2
from __future__ import print_function
import sys

sys.path.append('/usr/realtime/rtai-py/')
import rtai
import ctypes


class scope_data_structure(ctypes.Structure):
    _fields_ = [
        ('time', ctypes.c_double),
        ('control', ctypes.c_double),
        ('feedback', ctypes.c_double),
    ]


task = rtai.rt_task_init_schmod(rtai.nam2num("LAT1"), 20, 0, 0, 0, 0XF)
rtai.rt_make_soft_real_time()
controller_output_mbx = rtai.rt_get_adr(rtai.nam2num("MBX1"))
plant_feedback_mbx = rtai.rt_get_adr(rtai.nam2num("MBX2"))

scope_data = scope_data_structure()
scope_mbx = rtai.rt_mbx_init(rtai.nam2num("MBX3"), ctypes.sizeof(scope_data))
plant_feedback = ctypes.c_double()
controller_output = ctypes.c_double()
u1, u2, y1, y2 = 0, 0, 0, 0
initial_timestamp = rtai.rt_get_cpu_time_ns()

while True:
    rtai.rt_mbx_receive(controller_output_mbx,
                        ctypes.byref(controller_output),
                        ctypes.sizeof(controller_output))
    u = float(controller_output.value)
    y = 1.941 * y1 - 0.9418 * y2 + 2.451 * 0.000001 * u1 + 2.402 * 0.000001 * u2
    plant_feedback.value = y
    scope_data.value = y
    scope_data.time = rtai.rt_get_cpu_time_ns() - initial_timestamp
    u1, u2, y1, y2 = u, u1, y, y1
    rtai.rt_mbx_send_if(plant_feedback_mbx,
                        ctypes.byref(plant_feedback),
                        ctypes.sizeof(plant_feedback))
    rtai.rt_mbx_send_if(scope_mbx,
                        ctypes.byref(scope_data),
                        ctypes.sizeof(scope_data))




