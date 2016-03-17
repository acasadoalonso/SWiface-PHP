#!/usr/bin/python 

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

dbpath ="/var/www/html/cucfiles/"
cucpath="/var/www/html/cuc/"


print "Generate .CUC files V1.0 from  " +cucpath+ "contest.db the unzip of the .CUCX file"
start_time = time.time()
local_time = datetime.datetime.now()
print "Time is now:", local_time				# print the time for information only
fl_date_time = local_time.strftime("%Y%m%d")			# get the local time
CUC_DATA = cucpath + "QSGP" + fl_date_time+'.cuc'		# name of the CUC to be generated
JSONFILE = cucpath + "QSGP" + fl_date_time+'.json'		# name of the CUC to be generated
print "CUC generated data file is: ", CUC_DATA, JSONFILE	# just a trace
datafile = open (CUC_DATA, 'w')					# open the output file
jsonfile = open (JSONFILE, 'w')					# open the output file
cuchdr   = open (cucpath + "LIVEhdr.txt", 'r')			# opend the header file
cuctail  = open (cucpath + "LIVEtail.txt", 'r')			# open the trailer file
eventname="LIVE Pyrenees"

conn=sqlite3.connect(dbpath+'contest.db')			# open th DB in read only mode
cursD=conn.cursor()						# cursor for the CONTESTANT table
cursP=conn.cursor()						# cursor for the PILOT table
print "From the contest.db ..."
print "Contest data:"
cursD.execute ('select * from CONTEST')
for row in cursD.fetchall():
    print row
    eventname=row[2]

print "Location data:"
cursD.execute ('select * from LOCATION')
for row in cursD.fetchall():
    print row

print "Pilot data:"
cursD.execute ('select * from PILOT')
for row in cursD.fetchall():
    print row

buf=cuchdr.read()						# start reading the header file
datafile.write(buf)						# copy into the output file

# Build the tracks

tracks=[]							# create the instance for the tracks 

#
# SeeYou database  contest.db contestant table SQUEMA
#

#CREATE TABLE contestant (id_contestant BIGINT NOT NULL, ref_class BIGINT DEFAULT NULL, version INTEGER NOT NULL, name VARCHAR(255) NOT NULL, club VARCHAR(255) DEFAULT NULL, team VARCHAR(255) DEFAULT NULL, aircraft_model VARCHAR(255) NOT NULL, contestant_number VARCHAR(8) DEFAULT NULL, aircraft_registration VARCHAR(32) DEFAULT NULL, handicap DOUBLE PRECISION DEFAULT NULL, pure_glider BOOLEAN NOT NULL, flight_recorders CLOB DEFAULT NULL, tag VARCHAR(255) DEFAULT NULL, not_competing BOOLEAN NOT NULL, status VARCHAR(19) DEFAULT NULL, created_at DATETIME DEFAULT NULL, updated_at DATETIME DEFAULT NULL, PRIMARY KEY(id_contestant));

#

pn=0								# number of pilots found
cursD.execute('select name, aircraft_model, contestant_number, aircraft_registration, flight_recorders, id_contestant from CONTESTANT')		# get all the glifers flying now 
for row in cursD.fetchall():					# search all the rows
    pname=row[0]						# flarmid is the first field
    type=row[1]							# get glider type
    cn=row[2]							# get the competition numbers
    regi=row[3]							# get the registration 
    idflarm=row[4]						# get the flarmID 
    idflarm=idflarm.rstrip('\n')
    idflarm=idflarm.rstrip('\r')
    idcont=row[5]						# get the global ID of the contestant 
    if pname == "":
	if idflarm in kpilot.kpilot:				# check if know the pilot because is our database kpilot.py
		pname=kpilot.kpilot[idflarm]			# in that case place the name of the pilot
    	else:
		pname="Pilot NN-"+str(pn)			# otherwise just say: NoName#
#   								write the Pilot detail
#   "Tpilot","",*0,"FLRDDE1FC","Ventus","EC-TTT","TT","",0,"",0,"",1,"",""		# the template to use

    pn +=1 
    buf='"' +pname+ '","",*0,"' +idflarm+ '","' +type+ '","' +regi+ '","' +cn+ '","",0,"",0,"",1,"",""\n' 	# write tha into the psuedo CUC file
    datafile.write(buf)						# write the pilot information into the pseudo CUC file
    rgb=0x111*pn						# the the RGB color
    ccc=hex(rgb)						# convert it to hex
    color="#"+ccc[2:]						# set the JSON color required

    cursP.execute("select nationality from PILOT where id_pilot = ? ", [idcont])		# set the tcountry from the PILOT table
    pil=cursP.fetchone()
    country=pil[0]
    ccc = pycountry.countries.get(alpha2=pil[0])
    country=ccc.alpha3
    tr={"trackId": "QSGP"+fl:dte_time+":"+idflarm, "pilotName": pname,  "competitionId": cn, "country": country, "aircraft": type, "registration": regi, "3dModel": "ventus2", "ribbonColors":[color]}
    tracks.append(tr)						# add it to the tracks
    print "P==>: ", idflarm, pname, country, regi, cn, type
# ----------  end of for

#       Build the turning points

#
# SeeYou database  contest.db point table SQUEMA
#
# CREATE TABLE point (id_point BIGINT NOT NULL, name VARCHAR(255) NOT NULL, latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL, type VARCHAR(16) NOT NULL, elevation DOUBLE PRECISION NOT NULL, distance DOUBLE PRECISION NOT NULL, course_in DOUBLE PRECISION NOT NULL, course_out DOUBLE PRECISION NOT NULL, oz_type VARCHAR(16) NOT NULL, oz_max_altitude DOUBLE PRECISION DEFAULT NULL, oz_radius1 INTEGER NOT NULL, oz_radius2 INTEGER DEFAULT NULL, oz_angle1 DOUBLE PRECISION NOT NULL, oz_angle2 DOUBLE PRECISION DEFAULT NULL, oz_angle12 DOUBLE PRECISION DEFAULT NULL, oz_move BOOLEAN NOT NULL, oz_line BOOLEAN NOT NULL, oz_reduce BOOLEAN NOT NULL, created_at DATETIME DEFAULT NULL, updated_at DATETIME DEFAULT NULL, PRIMARY KEY(id_point));

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
	if   (wtyp == "start"):
		type="Start"
		oz="Line"
	elif (wtyp == "finish"):
		type="Finish"
		oz="Cylinder"
	else:
		type="Turnpoint"
		oz="Cylinder"
	lati= math.degrees(lati)
	long= math.degrees(long)
	tpx={"latitude": lati, "longitude": long, "name": name, "observationZone": oz, "type": type, "radius": ozra, "trigger":"Enter"}
	tp.append(tpx)
    	print "W==>: ", name, lati, long, alti, type, ozra
#	C4238680N00186830ELa Cerdanya - LECD
	f=lati - int(lati)
	f=int(f)*10000
	buf='C'+("%02d"%int(lati))+("%05d"%f)
	if (lati > 0.0):
		buf += 'N'
	else:
		buf += 'S'
	f=long - int(long)
	f=int(f)*10000
	buf +=("%02d"%int(long))+("%05d"%f)
	if (long > 0.0):
		buf += 'E'
	else:
		buf += 'W'
    	datafile.write(buf)						# write the pilot information into the pseudo CUC file
# 								TP templates


# event

event={"name": eventname, "description" : eventname, "taskType": "SailplaneGrandPrix", "startOpenTs": 0, "turnpoints": tp,  "tracks": tracks}
j=json.dumps(event, indent=4)
jsonfile.write(j)


# write the day entry

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

# wite the trailer in order to complete the format of the .CUC file

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
if pn == 0:
	print "No pilots found ... CUC invalid"
	exit(-1)
else:
	print "Pilots found ... ", pn
	exit(0)
