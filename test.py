#!/usr/bin/python2

import sys

sys.path.append('/usr/realtime/rtai-py/')
import ctypes
import time
import numpy as np
import matplotlib.pyplot as plt

plt.axis([0, 1000, 0, 1])
plt.ion()
i = 0

while (True):
    i = i + 0.005
    y = np.random.random()
    plt.scatter(i, y)
    plt.draw()
	
