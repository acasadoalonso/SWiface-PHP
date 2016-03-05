#!/usr/bin/python
#
# Silent Wings interface --- JSOn formaat
#
import json
import time
eg=[{'name':'QSGP', 'description':'QSGP La Cerdanya - Spain', 'events': [{'id':1, 'startOpenTs': 12345}]}]
#print eg
#print eg[0]['events'][0]['startOpenTs']
eg[0]['events'][0]['startOpenTs'] = int(time.time())
j=json.dumps(eg, indent=4)
print j
