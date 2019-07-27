#!/usr/bin/python3
#
# SGP scoring interface --- JSON formaat
#
import MySQLdb
import json
import sqlite3
import datetime
import time
import sys
import os
import config

dbpath = config.DBpath
# use the configuration DB path
DBpath = config.DBpath
# use the configuration DB name
DBname = config.DBname
# use the configuration DB table
DBtable = config.DBtable

#
#   This script looks into the SWiface database and generates  the fixes to Silent Wing studio
#

trackid = sys.argv[1]
since = sys.argv[2]
live = True
localtime = datetime.datetime.now()
today = localtime.strftime("%y%m%d")
date = "0"
time = "0"

if (since == "-1"):
    date = today
elif (since == "0"):
    date = today

else:
    datetimes = datetime.datetime.utcfromtimestamp(int(since))
    date = datetimes.strftime("%y%m%d")
    time = datetimes.strftime("%H%M%S")


if (today != date):                                             # it is today
    # no user archive folder
    dbpath = dbpath+'/archive/'
    live = False                                              # mark as NOT live
if (config.MySQL):
    conn = MySQLdb.connect(host=config.DBhost, user=config.DBuserread, passwd=config.DBpasswdread,
                           db=DBname, connect_timeout=1000)     # connect with the database
else:
    # open th DB in read only mode
    filename = DBpath+config.SQLite3
    fd = os.open(filename, os.O_RDONLY)
    conn = sqlite3.connect('/dev/fd/%d' % fd)
# cursor for the ogndata table
cursD = conn.cursor()

print((trackid, since,  date, time))

if (since == "-1"):                                             # if no timme since showw all
    cursD.execute("select date, time, longitude, latitude, altitude, idflarm  from OGNDATA where date = '" +
                  str(date)+"'")                                # get all the glifers flying now
elif (since == "0"):                                            # if no timme since showw all
    cursD.execute("select date, time, longitude, latitude, altitude  from OGNDATA where idflarm = '" +
                  trackid+"' and date = '"+str(date)+"'")                                # get all the glifers flying now
else:
    cursD.execute("select date, time, longitude, latitude, altitude  from OGNDATA where idflarm = ? and date = ? and time > ? ", [
                  trackid, date, time])           # get all the glifers flying now
tn = 0
#tracks=[{"t":0, "n":0, "e":0, "a":0}]
tracks = []

for row in cursD.fetchall():
    date = row[0]
    y = int(date[0:2])+2000
    M = int(date[2:4])
    d = int(date[4:6])
    time = row[1]
    h = int(time[0:2])
    m = int(time[2:4])
    s = int(time[4:6])
    dt = datetime.datetime(y, M, d, h, m, s)
    ts = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    lon = row[2]
    lati = row[3]
    alti = row[4]
    #print "T==>", tn, date, time, trackid, lati, long, alti, dt, ts
    if (since == '-1'):
        idflarm = row[5]
        tracks.append({"idflarm": idflarm, "t": int(ts),
                       "e": lon, "n": lati, "a": alti})
    else:
        tracks.append({"t": int(ts), "e": lon, "n": lati, "a": alti})
    tn += 1

tp = {"trackId": trackid, "live": live, "track": tracks}
j = json.dumps(tp, indent=4)
print (j)
if (config.MySQL):
    conn.close()
else:
    conn.close()
    os.close(fd)
