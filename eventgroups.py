#!/usr/bin/python
#
# Silent Wings interface --- JSOn formaat
#
import json
import time
eg1=[{'name':'QSGP', 'description':'QSGP La Cerdanya - Spain',   'events': [{'id':"QSGP", 'startOpenTs': int(time.time())}]}]
eg2=[{'name':'LIVE', 'description':'Live tracking in Pyrenees', 'events': [{'id':"LIVE", 'startOpenTs': int(time.time())}]}]
eg=eg1
eg=eg2
#print eg
#print eg[0]['events'][0]['startOpenTs']
#eg[0]['events'][0]['startOpenTs'] = int(time.time())
j=json.dumps(eg, indent=4)
print j
