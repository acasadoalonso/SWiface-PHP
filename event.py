#!/usr/bin/python
#
# Silent Wings interface --- JSON formaat
#
import json
import time
import sys
import os
import kpilot
import sqlite3
import MySQLdb
import datetime
import config

cucpath="./cuc/" 
#
#   This script looks into the SWiface database and generates  the fixes to Silent Wing studio
#
arg1=sys.argv[1]
id=arg1[0:4]								# first 4 chars either QSGP/CNVV or LIVE
eventid=arg1[0:]							# the argument is the event ID
dateid=eventid[6:12]							# the date is part of the event id
localtime=datetime.datetime.now()					# get today's date
today=localtime.strftime("%y%m%d")					# in string format yymmdd
DBpath=config.DBpath							# use the configuration DB path
DBname=config.DBname							# use the configuration DB name

if (today != dateid):
        DBpath=DBpath+'/archive/'					# use the archive folder instead
        DBname='SWARCHIVE'

if (id == "LIVE"):							# if it a dummy envent LIVE

#	Build the turning points

	tp=[]								# instance for the TP

# Build the tracks 							# instance for the tracks
	tracks=[]

#
	if (config.MySQL):
		conn=MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpasswd, db=DBname, connect_timeout=1000)     # connect with the database
	else:
		filename=DBpath+config.SQLite3		                # open th DB in read only mode
		fd = os.open(filename, os.O_RDONLY)
		conn = sqlite3.connect('/dev/fd/%d' % fd)
	cursD=conn.cursor()                                             # cursor for the ogndata table
	cursG=conn.cursor()                                             # cursor for the glider table
	pn=0                                                            # number of pilots found
	cmd="select distinct idflarm from OGNDATA where date = '"+dateid+"' order by GETDISTANCE('"+config.loclatitude+"','"+config.loclongitud+"', latitude, longitude) ASC LIMIT 0,32 ;" 
	#cmd="select distinct idflarm from OGNDATA where date = '"+dateid+"' LIMIT 0,32 ;" 
	#print cmd
	cursD.execute(cmd)
	for row in cursD.fetchall():                                    # search for the first 20 the rows
		idflarm=row[0]                                          # flarmid is the first field
		idf=idflarm[3:9]                                        # we skip the first 3 chars
		country="ESP"						# by deafult SPAIN 
		cursG.execute("select registration, cn, type from GLIDERS where idglider = '%s';" % idf)               # search now into the gliding database
		gli=cursG.fetchone()                                    # get the data from the DB
		if gli and gli != None:                                 # did we find it ??? Index is unique, only one row
			regi=gli[0]                                     # get the registration
			cn=gli[1]                                       # get the competition numbers
			if cn == "" or cn == " ":			# if not competition number, use the last two letter of the registration 
				cn=regi[4:6]                            # if none ?
			type=gli[2]                                     # get glider type
			if   regi[0:1] == "F":
				country="FRA"
			elif regi[0:1] == "D":
				country="GER"
			elif regi[0:1] == "G":
				country="GBR"
			elif regi[0:1] == "I":
				country="ITA"
			elif regi[0:2] == "OO":
				country="BEL"
			elif regi[0:2] == "OE":
				country="AUT"
			elif regi[0:2] == "HB":
				country="CHE"
			elif regi[0:2] == "CC":
				country="CHL"
			elif regi[0:2] == "PH":
				country="NLD"
			elif regi[0:2] == "ZS":
				country="ZAF"
		else:
			regi='NO-NAME'					# just indicate no name
			cn=str(pn)					# the CN is the pilot number found 
			type='NOTYPE'					# No glider type
			continue
		if idflarm in kpilot.kpilot:                            # check if know the pilot because is our database kpilot.py
			pname=kpilot.kpilot[idflarm]                    # in that case place the name of the pilot
		else:
			if regi == 'NO-NAME':				# if the gliders is not registered on the DDB
				pname="Pilot NN-"+str(pn)               # otherwise just say: NoName#
			else:
				pname=regi				# use the registration as pilot name 
#    		print "D==>: ", idflarm, pname, regi, cn, type
#                                                               write the Pilot detail

		pn +=1
    
		tr={"trackId": eventid+':'+idflarm, "pilotName": pname,  "competitionId": cn, "country": country, "aircraft": type, "registration": regi, "3dModel": "ventus2", "ribbonColors":["red"]}
		tracks.append(tr)

# event 
	y=int(eventid[4:8])                                             # year
	m=int(eventid[8:10])                                            # month
	d=int(eventid[10:12])                                           # day
	td=datetime.datetime(y,m,d)-datetime.datetime(1970,1,1)         # number of second until beginning of the day
	ts=int(td.total_seconds()+9*60*60)                              # timestamp 09:00:00 UTC
	event={"name": eventid, "description" : config.eventdesc2,  "eventRevision": 0, "task": { "taskType": "SailplaneGrandPrix", "startOpenTs": ts, "turnpoints" : config.tp },  "tracks": tracks}
	j=json.dumps(event, indent=4)
	
	conn.close()
else:									# in the case of the QSGP event just read the JSON file generated by the cup utility
	fname=cucpath+eventid+".json"					# name of the file on the cuc directory
	#print fname
	try:
		fd=open(fname, 'r')
		j=fd.read()
		fd.close()
	except:
		j=json.dumps(config.QSGP, indent=4)
		#print "Not found...", fname
print j
if ( not config.MySQL):
        os.close(fd)


