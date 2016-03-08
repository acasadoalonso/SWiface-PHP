#!/usr/bin/python
#
# Silent Wings interface --- JSON formaat
#
import sys
import json
import sqlite3
import datetime
import time
import sys
import os
from pytz       import timezone

TIMEZONE="CET"				#  <=== change this to the appropiate time zone.
#TIMEZONE="CEST"			#  <=== change this to the appropiate time zone.

#
#   This script looks into the SWiface database and generates  the fixes to Silent Wing studio
#

trackid=sys.argv[1]
since  =sys.argv[2]
#dt=datetime.datetime(1970,1,1)
#cet=timezone(TIMEZONE)
#lt=cet.localize(dt)
#offset=lt.utcoffset()
#nsec=offset.total_seconds()

if (since == "0"):
	date=0;
	time=0;
        dbpath='/nfs/OGN/SWdata/';
else:
	datetimes=datetime.datetime.utcfromtimestamp(int(since))
	date=     datetimes.strftime("%y%m%d")
	time=     datetimes.strftime("%H%M%S")
	#print trackid, since, date, time
	localtime=datetime.datetime.now()
	today=localtime.strftime("%y%m%d")
	if (today == date):
        	dbpath='/nfs/OGN/SWdata/';
	else:
       		dbpath='/nfs/OGN/SWdata/archive/';

#print since, dbpath, date, time
conn=sqlite3.connect(dbpath+'SWiface.db')                       # open th DB in read only mode
cursD=conn.cursor()                                             # cursor for the ogndata table
if (since == "0"):						# if no timme since showw all
	cursD.execute("select date, time, longitude, latitude, altitude  from OGNDATA where idflarm = ? ", [trackid])           # get all the glifers flying now
else:
	cursD.execute("select date, time, longitude, latitude, altitude  from OGNDATA where idflarm = ? and date = ? and time > ? ", [trackid, date, time])           # get all the glifers flying now
tn=0
#tracks=[{"t":0, "n":0, "e":0, "a":0}]
tracks=[]

for row in cursD.fetchall(): 
	date=row[0]
	y=int(date[0:2])+2000
	M=int(date[2:4])
	d=int(date[4:6])
	time=row[1]
	h=int(time[0:2])
	m=int(time[2:4])
	s=int(time[4:6])
	dt=datetime.datetime(y,M,d,h,m,s)
	ts=(dt - datetime.datetime(1970, 1, 1)).total_seconds()
	long=row[2]
	lati=row[3]
	alti=row[4]
	#print "T==>", tn, date, time, trackid, lati, long, alti, dt, ts
	tracks.append({"t": int(ts), "e":long, "n":lati, "a":alti})
	tn +=1

tp={"trackId": trackid, "live": True, "track": tracks}
j=json.dumps(tp, indent=4)
print j
conn.commit()
conn.close()

