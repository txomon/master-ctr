from __future__ import print_function
import random
try:
    import simplejson as json
except ImportError:
    import json
import time

__author__ = 'javier'

data = {
    'time': 1.0,
    'setpoint': random.random(),
    'feedback': random.random(),
}
while True:
    time.sleep(0.1)
    data['time'] += 1
    data['setpoint'] = random.random()
    data['feedback'] = random.random()
    print('{"type": "scope", "message":' + json.dumps(data) + '}')
