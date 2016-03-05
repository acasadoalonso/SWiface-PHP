#!/usr/bin/python
#
# Silent Wings interface --- JSON formaat
#
import sys
import json
import time

import sqlite3
import datetime
import time
import sys
import os

trackid=sys.argv[1]
since  =sys.argv[2]
date=since[0:6]
time=since[6:12]
print trackid, since, date, time

#
#   This script looks into the SWiface database and generates  the fixes to Silent Wing studio

dbpath ="/nfs/OGN/SWdata/"

conn=sqlite3.connect(dbpath+'SWiface.db')                       # open th DB in read only mode
cursD=conn.cursor()                                             # cursor for the ogndata table
cursD.execute("select date, time, longitude, latitude, altitude  from OGNDATA where date = ? and time > ?", [date, time])           # get all the glifers flying now
row = cursD.fetchall()
tn=0
tracks=[{"n":0, "e":0, "a":0}]
for row in cursD.fetchall(): 
	date=row[0]
	time=row[1]
	long=row[2]
	lati=row[3]
	alti=row[4]
	tracks[tn]={"n":longi, "e":lati, "a":alti}
	print "T==>", trackid, lati, long, alti
	tn +=1

tp={"trackid": trackid, "live": True, "tracks": tracks}
j=json.dumps(tp, indent=4)
print j
conn.commit()
conn.close()

