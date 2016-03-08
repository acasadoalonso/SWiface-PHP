#!/usr/bin/python
#
# Silent Wings interface --- JSON formaat
#
import json
import time
eg=[]							# create the event group
eg1={'name':'QSGP', 'description':'QSGP La Cerdanya - Spain',      'events': [{'id':"QSGP", 'startOpenTs': int(time.time())}]}
eg2={'name':'LIVE', 'description':'OGN Live tracking in Pyrenees', 'events': [{'id':"LIVE", 'startOpenTs': int(time.time())}]}
eg.append(eg1)						# append the individual events
eg.append(eg2)						# so far the QSGP and the LIVE
j=json.dumps(eg, indent=4)				# convert it to JSON format
print j							# pass it to the PHP script
