#!/usr/bin/python3
#
# Silent Wings interface --- JSON format
#
version='2.0'							# august 2026
import json
import sqlite3
import MySQLdb
import datetime
import time
import sys
import os
import config
from   gistfuncs  import unobscure
from   dtfuncs  import naive_utcnow, naive_utcfromtimestamp

#
#   This script looks into the SWiface database and generates  the fixes to Silent Wing studio
#

id = sys.argv[1]
trackid = id[id.find(':')+1:]
eventid = id[0:12]
since = sys.argv[2]
live = True
alltracks= False
DBname = config.DBname

date = "0"
time = "0"
if trackid[0:3] == 'ALL' or trackid[0:3] == 'all':		# check if it is a request for all tracks
   alltracks=True
localtime = datetime.datetime.now()

today = naive_utcnow().strftime("%y%m%d")			# utc date in YYMMDD format
if (since == "0"):						# at the beginning
    date = eventid[6:12]					# get the date from the eventid SGPFyyyymmdd

else:								# else the date/time is on the Unixtime
    datetimes = datetime.datetime.utcfromtimestamp(
        int(since))  						# time converted from UNIX timestamp
    date = datetimes.strftime("%y%m%d")				# date converted
    time = datetimes.strftime("%H%M%S")				# time converted
    								# UTC time minus 30 seconds for buffering
    datetimet = datetime.datetime.utcnow() - datetime.timedelta(0, 30)
    timet = datetimet.strftime("%H%M%S")			# UTC now  minus 30 seconds


DBtable     = config.DBtable					# table name default OGNDATA
DTarchive   = getattr(config, 'DTarchive',   'OGNDATAARCHIVE')	# archive table name default OGNDATAARCHIVE
if (today != date):						# it is today ?
    live = False						# mark as NOT live
    timet=time							# if not live no needed to reduce time by 30 seconds
    DBtable=DTarchive						# use the archive table instead of the live table

dbpath = config.DBpath						# use the std path

#print trackid,":", eventid,":", since,":", date,":", time

# 
# open the database
#

if (config.MySQL):						# Are we using MySQL ??
    conn = MySQLdb.connect(host=config.DBhost, user=config.DBuserread,
                           passwd=unobscure(config.DBpasswdread).decode(),
                           db=DBname )     		# connect with the database
else:							# SQLIte

    							# open th DB in read only mode
    filename = dbpath + config.SQLite3 
    fd = os.open(filename, os.O_RDONLY)			# open the file
    conn = sqlite3.connect('/dev/fd/%d' % fd)		# connect with the database

# cursor for the ogndata table
cursD = conn.cursor()					# cursor to be used
if (since == "0" and not alltracks):			# if no timme since showw all
    cursD.execute("select date, time, longitude, latitude, altitude, idflarm  from "+DBtable +
                  " where idflarm = '%s' and date = '%s' order by time limit 1000;" % (trackid, date))   # get all the positions now
elif (since == "0" and alltracks):			# if no timme since showw all
    cursD.execute("select date, time, longitude, latitude, altitude, idflarm  from "+DBtable +
		  " where date = '%s' order by time limit 1000;" % (date))   # get all the positions now
elif alltracks:
    cursD.execute("select date, time, longitude, latitude, altitude, idflarm  from "+DBtable +
                  " where date = '%s' and time > '%s' and time <= '%s'  order by time" % (date, time, timet))
else:
    cursD.execute("select date, time, longitude, latitude, altitude, idflarm  from "+DBtable +
                  " where idflarm = '%s' and date = '%s' and time > '%s' and time <= '%s'  order by time" % (trackid, date, time, timet))

tn = 0
rows=cursD.fetchall()
nrows=len(rows)
#print("NRows", nrows)
#tracks=[{"t":0, "n":0, "e":0, "a":0, "id":0}]			# the track information
tracks = []							# the track information

for row in rows: 						# get all the records from the DDBB
    date = row[0]						# date in YYMMDD format
    y = int(date[0:2])+2000					# convert from YYMMDD HHMMSS to UNIX time
    M = int(date[2:4])
    d = int(date[4:6])
    time = row[1]						# time in HHMMSS format		
    h = int(time[0:2])
    m = int(time[2:4])
    s = int(time[4:6])
    dt = datetime.datetime(y, M, d, h, m, s)
    # Unix time, seconds from the epoch
    ts = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    lon = row[2]						# longitude
    lati = row[3]						# latitude
    alti = row[4]						# altitude
    idfl = row[5]						# idflarm
    #print "T==>", tn, date, time, trackid, lati, lon, alti, dt, ts
    if alti == 0:
        # append it to the previous record, no altitude
        tracks.append({"t": int(ts), "e": lon, "n": lati, "id": idfl})
    else:
        # append it to the previous record
        tracks.append({"t": int(ts), "e": lon, "n": lati, "a": alti, "id": idfl})
    tn += 1							# increment the track number

if nrows > 0:							# if there are records, build the JSON record
   tp = {"trackId": id, "live": live, "track": tracks}		# build the JSON record
else:								# if no records, build the JSON record with heartbeat	
   tp = {"trackId": id, "live": live, "track": tracks, "heartbeat": since }		

j = json.dumps(tp, indent=4)					# convert from dict to JSON
print(j)							# print the JSON record
conn.close()							# close DDBB connection
if (not config.MySQL):						# if SQLite3
    os.close(fd)						# just close the file
# --------------------------------------------------------------#

