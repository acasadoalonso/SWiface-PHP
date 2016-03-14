#!/usr/bin/python
#
# Silent Wings interface --- JSON formaat
#
import json
import time
import datetime
import os

today=datetime.date.today()
yesterday=datetime.date(today.year, today.month, today.day -1)

evQ=[]							# create the event entity
evL=[]							# new instance of the event
eg=[]							# create the event group

ev1={'id':"QSGP-Today", 'startOpenTs': int(time.time())}# Today's Day event
evQ.append(ev1)						# add the basic event

ev2={'id':"LIVE-today", 'startOpenTs': int(time.time())}# Live today's event
evL.append(ev2)						# add today's event
#ev3={'id':"LIVE-yesterday", 'startOpenTs': int(time.time()-86400)}
#evL.append(ev3)						# add yesterday's event


cuc=os.listdir('cuc')					# scan the cuc directory
for fn in cuc:
	ft=fn[fn.find('.')+1:]				# file type
	fb=fn[0:fn.find('.')]				# file base name
	if (ft == 'cuc'):				# only .cuc files
		LQ=fn[0:4]				# either LIVE or QSGP for the time being
		y=int(fn[4:8])				# year
		m=int(fn[8:10])				# month
		d=int(fn[10:12])			# day
 		td=datetime.datetime(y,m,d)-datetime.datetime(1970,1,1) # number of second until beginning of the day
		ts=td.total_seconds()			# timestamp
		ex3={'id':fb , 'startOpenTs': int(ts)}
		if (LQ == "LIVE"):			# if LIVE event
			evL.append(ex3)			# add this event to the LIVE event group
		else:
			evQ.append(ex3)			# add this event to the QSGP event group

# create the event groups

eg1={'name':'QSGP', 'description':'QSGP La Cerdanya - Spain', 'events': evQ}
eg2={'name':'OGN LIVE', 'description':'OGN Live tracking in Pyrenees', 'events': evL}
eg.append(eg1)						# append the individual events groups
eg.append(eg2)						# so far the QSGP and the LIVE
j=json.dumps(eg, indent=4)				# convert it to JSON format
print j							# pass it to the PHP script
exit()

