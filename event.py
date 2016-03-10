#!/usr/bin/python
#
# Silent Wings interface --- JSON formaat
#
import json
import time
import sys
import QSGP
import kpilot
import sqlite3
import datetime

dbpath= "/nfs/OGN/SWdata/"
cucpath="/var/www/cuc/" 

#
#   This script looks into the SWiface database and generates  the fixes to Silent Wing studio
#
eventid=sys.argv[1]

if (eventid == "LIVE"):							# if it a dummy envent LIVE

#	Build the turning points

	tp=[]
	tp.append(QSGP.tp1)
	tp.append(QSGP.tp2)
	tp.append(QSGP.tp3)

# Build the tracks 
	tracks=[]

#
	conn=sqlite3.connect(dbpath+'SWiface.db')                       # open th DB in read only mode
	cursD=conn.cursor()                                             # cursor for the ogndata table
	cursG=conn.cursor()                                             # cursor for the glider table
	pn=0                                                            # number of pilots found
	cursD.execute('select distinct idflarm from OGNDATA')           # get all the glifers flying now
	for row in cursD.fetchall():                                    # search all the rows
    		idflarm=row[0]                                          # flarmid is the first field
    		idf=idflarm[3:9]                                        # we skip the first 3 chars
    		cursG.execute("select registration, cn, type from GLIDERS where idglider = ?", [idf])               # search now into the gliding database
    		gli=cursG.fetchone()                                    # get the data from the DB
    		if gli and gli != None:                                 # did we find it ??? Index is unique, only one row
                	regi=gli[0]                                     # get the registration
                	cn=gli[1]                                       # get the competition numbers
                	if cn == "":
                        	cn="XX"                                 # if none ?
       	        	type=gli[2]                                     # get glider type
    		else:
                	regi='NO-NAME'
                	cn='NN'
                	type='NOTYPE'
    		if idflarm in kpilot.kpilot:                            # check if know the pilot because is our database kpilot.py
        		pname=kpilot.kpilot[idflarm]                    # in that case place the name of the pilot
    		else:
        		pname="Pilot NN-"+str(pn)                       # otherwise just say: NoName#
#    		print "D==>: ", idflarm, pname, regi, cn, type
#                                                               write the Pilot detail

    		pn +=1
    
		tr={"trackId": idflarm, "pilotName": pname,  "competitionId": cn, "country": "ES", "aircraft": type, "registration": regi, "3dModel": "ventus2", "ribbonColors":["red"]}
		tracks.append(tr)

# event 

	event={"name": eventid, "description" : "LIVE Pyrenees", "taskType": "SailplaneGrandPrix", "startOpenTs": 0, "turnpoints": tp,  "tracks": tracks}
	j=json.dumps(event, indent=4)
else:
	datetimes=datetime.datetime.now()
	fname=cucpath+eventid+datetimes.strftime("%Y%m%d")+".json"
	try:
		fd=open(fname, 'r')
		j=fd.read()
		fd.close()
	except:
		j=json.dumps(QSGP.QSGP, indent=4)
		#print "Not found...", fname
print j
