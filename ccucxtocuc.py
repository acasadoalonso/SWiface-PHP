#!/usr/bin/python 
# -*- coding: UTF-8 -*-
#
#   This script converts a .CUCX files to be .CUC (old format)
#


import sqlite3
import datetime
import time
import sys
import os
import kpilot
import QSGP
import json
import math
import pycountry
import config
#-------------------------------------------------------------------------------------------------------------------#

def fixcoding(addr):
        if addr != None:
                addr=addr.replace(u'á', u'a')
                addr=addr.replace(u'à', u'a')
                addr=addr.replace(u'â', u'a')
                addr=addr.replace(u'Á', u'A')
                addr=addr.replace(u'é', u'e')
                addr=addr.replace(u'è', u'e')
                addr=addr.replace(u'ê', u'e')
                addr=addr.replace(u'É', u'E')
                addr=addr.replace(u'í', u'i')
                addr=addr.replace(u'ì', u'i')
                addr=addr.replace(u'î', u'i')
                addr=addr.replace(u'Í', u'I')
                addr=addr.replace(u'ó', u'o')
                addr=addr.replace(u'ò', u'o')
                addr=addr.replace(u'ô', u'o')
                addr=addr.replace(u'Ó', u'O')
                addr=addr.replace(u'Ò', u'O')
                addr=addr.replace(u'ú', u'u')
                addr=addr.replace(u'ù', u'u')
                addr=addr.replace(u'û', u'u')
                addr=addr.replace(u'Ú', u'U')
                addr=addr.replace(u'ü', u'u')
                addr=addr.replace(u'ñ', u'n')
                addr=addr.replace(u'Ñ', u'N')
                addr=addr.replace(u'Ø', u'O')
        return addr


dbpath ="./cucfiles/"
cucpath="./cuc/"
eventname="LIVE Pyrenees"					# TODO: Why is this initialized here?
taskType="SailplaneRacing"

# 
# to run this program, first copy the .CUCX fiile into the cucfiles direcory and unzip that file.
#

print "Generate .CUC files V1.0 from  " +cucpath+ "contest.db the unzip of the .CUCX file"
start_time = time.time()
local_time = datetime.datetime.now()
print "Time is now:", local_time				# print the time for information only
fl_date_time = local_time.strftime("%Y%m%d")			# get the local time
CUC_DATA = cucpath + config.Initials + fl_date_time+'.cuc'		        # name of the CUC to be generated
JSONFILE = cucpath + config.Initials + fl_date_time+'.json'		# name of the CUC to be generated
print "CUC generated data file is: ", CUC_DATA, JSONFILE	# just a trace
datafile = open (CUC_DATA, 'w')					# open the output file
jsonfile = open (JSONFILE, 'w')					# open the output file
cuchdr   = open (cucpath + "LIVEhdr.txt", 'r')			# opend the header file
cuctail  = open (cucpath + "LIVEtail2.txt", 'r')		# open the trailer file


conn =sqlite3.connect(dbpath+'contest.db')			# open the DB embedded into the .CUCX file unzipped 
connG=sqlite3.connect(config.DBpath+config.DBname)			        # open the DB with all the GLIDERS information
cursG =connG.cursor()						# cursor for the GLIDERS table
cursD =conn.cursor()						# cursor for the CONTESTANT table
cursP =conn.cursor()						# cursor for the PILOT table
print "From the contest.db ..."
print "Contest data:"
cursD.execute ('select * from CONTEST')				# get the CONTEST data information
for row in cursD.fetchall():
    print row
    eventname=row[2]

print "Location data:"
cursD.execute ('select * from LOCATION')			# get the LOCATION information
for row in cursD.fetchall():
    print row
    

print "Pilot data:"
cursD.execute ('select * from PILOT')				# and all the pilots
for row in cursD.fetchall():
    print row

print "Contestant data:"
cursD.execute ('select * from CONTESTANT')			# and all the pilots/contestant
for row in cursD.fetchall():
    print row

print "Waypoint information:"
cursD.execute ('select * from POINT')				# and all the pilots/contestant
for row in cursD.fetchall():
    print row

# --------------------------------------------------------------

buf=cuchdr.read()						# start reading the pseudo CUC header file
datafile.write(buf)						# copy into the output file

# Build the tracks

tracks=[]							# create the instance for the tracks 

#
# SeeYou database  contest.db contestant table SQUEMA
#

#CREATE TABLE contestant (id_contestant BIGINT NOT NULL, ref_class BIGINT DEFAULT NULL, version INTEGER NOT NULL, name VARCHAR(255) NOT NULL, club VARCHAR(255) DEFAULT NULL, team VARCHAR(255) DEFAULT NULL, aircraft_model VARCHAR(255) NOT NULL, contestant_number VARCHAR(8) DEFAULT NULL, aircraft_registration VARCHAR(32) DEFAULT NULL, handicap DOUBLE PRECISION DEFAULT NULL, pure_glider BOOLEAN NOT NULL, flight_recorders CLOB DEFAULT NULL, tag VARCHAR(255) DEFAULT NULL, not_competing BOOLEAN NOT NULL, status VARCHAR(19) DEFAULT NULL, created_at DATETIME DEFAULT NULL, updated_at DATETIME DEFAULT NULL, PRIMARY KEY(id_contestant));

#
pn=0                                                            # number of pilots found

nwarnings=0                                                     # number of warnings
                                                                # get the pilot information from the contestant table
cursD.execute('select name, aircraft_model, contestant_number, aircraft_registration, flight_recorders, id_contestant from CONTESTANT')
                                                                # get all the CONTESTAN pilots
for row in cursD.fetchall():					# search all the rows
	
	pname=row[0]						# pilot name  is the first field
	pname=fixcoding(pname).encode('utf8')                   # fix the UTF8 coding
	if row[1]:
		type=row[1]					# get glider type
	else :
		type="type_NOTYET"
	if row[2]:
		cn=row[2]                                       # get the competition numbers
	else:
		cn="cn_NOTYET"
	if row[3]:
		regi=row[3]                                     # get the registration 
	else:
		regi="EC-XXX"                                   # dummy reg
	if row[4]:	
		idflarm=row[4]					# get the flarmID
								# check for FLARMID	
		idflarm=idflarm.rstrip('\n')
		idflarm=idflarm.rstrip('\r')
	else:
		idflarm = "*"                                   # mark it as not found
                                                                # try to get it from the OGN database
		cursG.execute('select * from GLIDERS where registration = ?', [regi])
		for rowg in cursG.fetchall():
			if rowg[0]:
				idflarm = "FLR"+rowg[0]
				
		
	idcont=row[5]						# get the global ID of the contestant
	
	if pname == "":                                         # if not pilot name ???        
		if idflarm in kpilot.kpilot:			# check if know the pilot because is our database kpilot.py
				pname=kpilot.kpilot[idflarm]	# in that case place the name of the pilot
		else:
				pname="Pilot NN-"+str(pn)	# otherwise just say: NoName#
#   								# write the Pilot detail
#   "Tpilot","",*0,"FLRDDE1FC","Ventus","EC-TTT","TT","",0,"",0,"",1,"","" # the template to use
#

	pn += 1                                                 # increase the number of pilots found
	
	buf='"' +pname+ '","",*0,"' +idflarm+ '","' +type+ '","' +regi+ '","' +cn+ '","",0,"",0,"",1,"",""\n' 	# write tha into the psuedo CUC file
	datafile.write(buf)					# write the pilot information into the pseudo CUC file
	rgb=0x111*pn						# the the RGB color
	ccc=hex(rgb)						# convert it to hex
	color="#"+ccc[2:]					# set the JSON color required

	cursP.execute("select nationality, igc_id from PILOT where id_pilot = ? ", [idcont])		# set the tcountry from the PILOT table
	pil=cursP.fetchone()
	country=pil[0]                                          # get the country of the pilot
	ccc = pycountry.countries.get(alpha_2=pil[0])           # convert it to the 3 chars ISO code
	country=ccc.alpha3
	if pil[1]:                                              # get the IGC ranking list ID
			igcid=pil[1]
	else:
			igcid=-1
			
	tr={"trackId": config.Initials+fl_date_time+":"+idflarm, "pilotName": pname,  "competitionId": cn, "country": country,\
            "aircraft": type, "registration": regi, "3dModel": "ventus2", "ribbonColors":[color], \
            "portraitUrl": "http://rankingdata.fai.org/PilotImages/"+str(igcid)+".jpg"}
	
	tracks.append(tr)					# add it to the tracks
	print "P==>: ", pname, idflarm, country, regi, cn, type, igcid, idcont
	if idflarm=="*":                                        # if not FLARM ID specified ???
			print "Warning", pname, regi, " NO Flarm ID"
			nwarnings +=1                           # increase the number of warnings
			
# ----------  end of for -----------------------*

#       Build the turning points                *
#       ========================                *

#
# SeeYou database  contest.db point table SQUEMA
#
# CREATE TABLE point (id_point BIGINT NOT NULL, name VARCHAR(255) NOT NULL, latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL, type VARCHAR(16) NOT NULL, elevation DOUBLE PRECISION NOT NULL, distance DOUBLE PRECISION NOT NULL, course_in DOUBLE PRECISION NOT NULL, course_out DOUBLE PRECISION NOT NULL, oz_type VARCHAR(16) NOT NULL, oz_max_altitude DOUBLE PRECISION DEFAULT NULL, oz_radius1 INTEGER NOT NULL, oz_radius2 INTEGER DEFAULT NULL, oz_angle1 DOUBLE PRECISION NOT NULL, oz_angle2 DOUBLE PRECISION DEFAULT NULL, oz_angle12 DOUBLE PRECISION DEFAULT NULL, oz_move BOOLEAN NOT NULL, oz_line BOOLEAN NOT NULL, oz_reduce BOOLEAN NOT NULL, created_at DATETIME DEFAULT NULL, updated_at DATETIME DEFAULT NULL, PRIMARY KEY(id_point));
#

tp=[]								# create the instance for the turn points

buf="V,HighEnl=300,AsViolate=True,MinFinAlt=0m,MaxFinAlt=10000m,MaxStartAlt=0m,MaxAlt=0m,MaxAltCorr=50.0m,AltTimeout=0,StartGsp=0km/h,FixRate=10,ValFailed=True"
datafile.write(buf)						# write the turn point information
buf="C301299000000301299000003"
datafile.write(buf)						# write the information of when the task was created

cursD.execute('select name, latitude, longitude , elevation, type, oz_type, oz_radius1 from POINT')		# get all the turning points of the task flying now 
for row in cursD.fetchall():					# search all the rows
	name=row[0];						# waypoint name
	lati=row[1];						# latutude
	long=row[2];						# longitude
	alti=row[3];						# altitude
	wtyp=row[4];						# waypoint type start/point/finish/none
	ozty=row[5];						# oz type: next/symmetric/previous
	ozra=row[6];						# oz radius
	if   (wtyp == "start"):                                 # change it to the format requested by SW
		type="Start"
		oz="Line"
	elif (wtyp == "finish"):
		type="Finish"
		oz="Cylinder"
	else:
		type="Turnpoint"
		oz="Cylinder"
	lati= math.degrees(lati)                                # change it from radians to DMS
	long= math.degrees(long)
	tpx={"latitude": lati, "longitude": long, "name": name, "observationZone": oz, "type": type, "radius": ozra, "trigger":"Enter"}
	tp.append(tpx)                                          # add it to the TP list
	print "W==>: ", name, lati, long, alti, type, ozra
#	C4238680N00186830ELa Cerdanya - LECD
	N=True
	if lati < 0:
		lati *=-1.0
		N=False
	f=lati - int(lati)
	f=int(f*100000.0)
	buf='C'+("%02d"%int(lati))+("%05d"%f)
	if (N):
		buf += 'N'
	else:
		buf += 'S'
	E=True
	if long < 0: 
		long *=-1.0
		E=False
	f=long - int(long)
	f=int(f*100000.0)
	buf +=("%03d"%int(long))+("%05d"%f)
	if (E):
		buf += 'E'
	else:
		buf += 'W'
	buf +=name
	buf +="\n"
	#print "Buf==>", buf
	datafile.write(buf)					# write the pilot information into the pseudo CUC file
# 								# TP templates

# event                                                         # create the event ...

event={"name": eventname, "description" : eventname, "taskType": taskType, "startOpenTs": 0, "turnpoints": tp,  "tracks": tracks}
j=json.dumps(event, indent=4)                                   # dump it in JSON format
jsonfile.write(j)                                               # write it to the JSON file 


# write the day entry                                           # finish the .CUC file 
#
# [Starts]							# this is the template
#
# [Day_02/03/2016]
# D02032016-010400000

datafile.write("[Starts]\n")					# write it in the output file
datafile.write(" \n")
buf="[Day_"+local_time.strftime("%d/%m/%Y")+"]\n"
datafile.write(buf)
buf="D" + local_time.strftime("%d%m%Y") + "-010400000\n"
datafile.write(buf)

# write the trailer in order to complete the format of the .CUC file

buf=cuctail.read()						# read the trailer file
datafile.write(buf)						# write it into the output file

#
# close the files and exit
#

datafile.close()
jsonfile.close()
cuchdr.close()
cuctail.close()
conn.commit()
conn.close()
connG.close()
if pn == 0 or nwarnings > 0:
	print "CUC invalid: No pilots found or warnings found ... ", pn, nwarnings
	exit(-1)
else:
	print "Pilots found ... ", pn
	exit(0)
