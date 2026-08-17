#!/usr/bin/python3
#
# Silent Wings interface --- JSON format
#
version='2.0'
import json
import sqlite3
import MySQLdb
import datetime
import time
import sys
import os
import config
from   gistfuncs  import unobscure
from dtfuncs  import naive_utcnow, naive_utcfromtimestamp

#
#   This script looks into the SWiface database and generates  the fixes to Silent Wing studio
#

id = sys.argv[1]
trackid = id[id.find(':')+1:]
eventid = id[0:12]
since = sys.argv[2]
live = True
DBname = config.DBname
DBtable = config.DBtable
if trackid[0:3] == 'ALL' or trackid[0:3] == 'all':
   alltracks=True
localtime = datetime.datetime.now()
today = localtime.strftime("%y%m%d")
today = naive_utcnow().strftime("%y%m%d")
date = "0"
time = "0"
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


if (today != date):						# it is today ?
    live = False						# mark as NOT live
    timet=time							# if not live no needed to reduce time by 30 seconds

dbpath = config.DBpath					# use the std path
#print trackid,":", eventid,":", since,":", date,":", time

# 
# open the database
#
###     DBarchive   = 'SWARCHIVE'          (MySQL)
###     SQLite3arch = 'archive/SWiface.db' (SQLite3)
DBarchive   = getattr(config, 'DBarchive',   'SWARCHIVE')
SQLite3arch = getattr(config, 'SQLite3arch', 'archive/' + config.SQLite3)

if (config.MySQL):						# Are we using MySQL ??
    conn = MySQLdb.connect(host=config.DBhost, user=config.DBuserread,
                           passwd=unobscure(config.DBpasswdread).decode(),
                           db=(DBname if live else DBarchive))     # connect with the database
else:							# SQLIte

    							# open th DB in read only mode
    filename = dbpath + (config.SQLite3 if live else SQLite3arch)
    fd = os.open(filename, os.O_RDONLY)			# open the file
    conn = sqlite3.connect('/dev/fd/%d' % fd)		# connect with the database

# cursor for the ogndata table
cursD = conn.cursor()					# cursor to be used
if (since == "0"):					# if no timme since showw all
    cursD.execute("select date, time, longitude, latitude, altitude  from "+DBtable +
                  " where idflarm = '%s' and date = '%s' order by time;" % (trackid, date))   # get all the positions now
elif alltracks:
    cursD.execute("select date, time, longitude, latitude, altitude  from "+DBtable +
                  " where date = '%s' and time > '%s' and time <= '%s'  order by time" % (date, time, timet))
else:
    cursD.execute("select date, time, longitude, latitude, altitude  from "+DBtable +
                  " where idflarm = '%s' and date = '%s' and time > '%s' and time <= '%s'  order by time" % (trackid, date, time, timet))

tn = 0
nrows=len(cursD.fetchall())
#tracks=[{"t":0, "n":0, "e":0, "a":0}]
tracks = []							# the track information

for row in cursD.fetchall(): 					# get all the records from the DDBB
    date = row[0]
    y = int(date[0:2])+2000					# convert from YYMMDD HHMMSS to UNIX time
    M = int(date[2:4])
    d = int(date[4:6])
    time = row[1]
    h = int(time[0:2])
    m = int(time[2:4])
    s = int(time[4:6])
    dt = datetime.datetime(y, M, d, h, m, s)
    # Unix time, seconds from the epoch
    ts = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    lon = row[2]						# longitude
    lati = row[3]						# latitude
    alti = row[4]						# altitude
    #print "T==>", tn, date, time, trackid, lati, lon, alti, dt, ts
    if alti == 0:
        # append it to the previous record, no altitude
        tracks.append({"t": int(ts), "e": lon, "n": lati})
    else:
        # append it to the previous record
        tracks.append({"t": int(ts), "e": lon, "n": lati, "a": alti})
    tn += 1

if nrows > 0:
   tp = {"trackId": id, "live": live, "track": tracks}		# build the JSON recorda
else:
   tp = {"trackId": id, "live": live, "track": tracks, "heartbeat": since }		# build the JSON record

j = json.dumps(tp, indent=4)					# convert from dict to JSON
print(j)
conn.close()							# close DDBB connection
if (not config.MySQL):						# if SQLite3
    os.close(fd)						# just close the file
# --------------------------------------------------------------#
