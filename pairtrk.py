#!/usr/bin/python
#
# Silent Wings interface --- JSON formaat
#
import json
import time
import sys
import os
import MySQLdb
import datetime
import urllib.parse
from  ognddbfuncs import *
import config

#
#   This script set the pairing between OGN trackers and flarms that are on the same glider, so it become a virtual single device
#

action='list'
trk='ALL'
tflarmid=''
towner=''
deleteyn='N'
#print (sys.argv)
if len(sys.argv) >1:
	arg1 = sys.argv[1]
	action = arg1[0:]				
if len(sys.argv) >2:
	arg2 = sys.argv[2]
	trk = arg2[0:9].upper()
if len(sys.argv) > 4:
	arg3 = sys.argv[3]
	tflarmid = arg3[0:9].upper()					
	arg4 = sys.argv[4]
	towner = arg4[0:]	
if len(sys.argv) > 6:
	arg5 = sys.argv[5]
	deleteyn = arg5[0:1].upper()					
	arg6 = sys.argv[6]
	active = arg6[0:1]					
#print (len(sys.argv), "Action=", action, "Tracker=", trk, "FlarmID=", tflarmid, "Owner=", towner, deleteyn)

localtime = datetime.datetime.now()					# get today's date
today = localtime.strftime("%y/%m/%d")					# in string format yymmdd
DBpath = config.DBpath							# use the configuration DB path
DBname = config.DBname							# use the configuration DB name
DBtable = config.DBtable						# use the configuration DB table
DBname ='APRSLOG'
DBtable = 'TRKDEVICES'

html1 = """<head><meta charset="UTF-8"></head><TITLE>Get the pairing of trackers with flarms</TITLE> <IMG src="./gif/ogn-logo-150x150.png" border=1 alt=[image]><H1>The pairing so far are: </H1> <HR> <P>Today is:  %s and we have %d Pairs on TRKDEVICES table.  <br/> Do you want to <a href=%s/SWS/pairtrkadd.html >Add a new pairing device: </a>  <br /> </p> </HR> """
html2 = """<center><table><tr><td><pre>"""
html3 = """</pre></td></tr></table></center>"""
html4 = '<a href='+config.SWSserver+'SWS/pairtrk.php?action=edit&trk=%s&flarmid=%s&owner=%s&active=%s'


#
conn = MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpasswd, db=DBname, connect_timeout=1000)     # connect with the database
cursD = conn.cursor()				# connect with the DB set the cursor
	
if action == 'update':				# the update order
	if trk[0:3] != 'OGN' and (tflarmid[0:3] == 'FLR' or tflarmid[0:3] == 'ICA'):	# check that we are pairing OGN to FLR/ICA
		print ("Pairing error, you can only pair OGN tracker with Flarms")
		conn.close()
		exit(1)
	if deleteyn == 'Y':			# if we want to delete the record
		cmd1 = "DELETE FROM "+DBtable+" WHERE id = '"+trk+"' ;"
	else:
		cmd1 = "UPDATE "+DBtable+" SET "	# if we want just to update the record
		if towner != '':
			cmd1 += " owner = '"+towner+"' , " 				# if updated the owner
		if active != '':
			cmd1 += " active = '"+active+"' , " 				# if updated the active
		if tflarmid != '':
			cmd1 += " flarmid = '"+tflarmid+"' WHERE id = '"+trk+"' ;" 	# or just the Flarmid
	#print (cmd1)
	if getognchk(trk[3:]) and getognchk(tflarmid[3:]):				# check that the devices are registered in order to be consistent
		try:
        		cursD.execute(cmd1)						# delete or update the DB
		except MySQLdb.Error as e:
        		print ("SQL error: ",e)
		conn.commit()
	else:										# warn about the error
		print ("UPDATE Pairing Error either the OGN tracker "+trk+" or the FlarmID "+tflarmid+" are not registered on the OGN DDB")
	conn.close()
	exit(0)

if action == 'add':				# adding a new pair ogn <==> flarm
	#print ("ADD Action=", action, "Tracker=", trk, "FlarmID", tflarmid, "Owner=", towner)
	if trk[0:3] != 'OGN' and (tflarmid[0:3] == 'FLR' or tflarmid[0:3] == 'ICA'):
		print ("Pairing error, you can only pair OGN tracker with Flarms")
		conn.close()
		exit(1)
	ognreg=getognreg(trk[3:])		# the the information fro the OGN DDB
	flrreg=getognreg(tflarmid[3:])		# glider registration
	cn=getogncn(tflarmid[3:])		# glider competition ID
	model=getognmodel(tflarmid[3:])		# glider model
	if getognchk(trk[3:]) and getognchk(tflarmid[3:]):				# checkk that the devices are rgistered on the OGN DDB
		cmd1 = "INSERT INTO "+DBtable+" (id, owner, spotid, compid, model, registration, active, devicetype, flarmid) VALUES ( '"+trk+"', '"+towner+"', '"+ognreg+"' , '"+cn+"', '"+model+"', '"+flrreg+"', '1', 'OGNT', '"+tflarmid+"' ) ; "
		#print ("cmd1:",cmd1)
		try:
        		cursD.execute(cmd1)
		except MySQLdb.Error as e:
        		print ("Pairing error, ID already exist on the DB --- SQL error: ",e)
		conn.commit()
	else:
		print ("ADD Pairing Error either the OGN tracker "+trk+" or the FlarmID "+tflarmid+" are not registered on the OGN DDB")
	conn.close()
	exit(0)

#
# action LIST ALL pair
#
cmd1 = "select count(*) from "+DBtable+" where devicetype = 'OGNT' ;"
try:
        cursD.execute(cmd1)
except MySQLdb.Error as e:
        print ("SQL error: ",e)
row = cursD.fetchone()
nrecs=row[0]
if trk == 'ALL':
	cmd1 = "select * from "+DBtable+" where id like '%OGN%' and devicetype = 'OGNT' ;"
else:
	cmd1 = "select * from "+DBtable+" where id = '"+trk+"' and devicetype = 'OGNT' ;"
#print cmd
try:
        cursD.execute(cmd1)
except MySQLdb.Error as e:
        print ("SQL error: ",e)

print (html1% (today,nrecs, config.SWSserver))
print (html2)
print ("<a> TRKDEV  IDTRK     REGTRK    REGIST  CID ACT DEVTYP Flarm     Owner </a>") 
for row in cursD.fetchall():                                    # search for the first 20 the rows
        # flarmid is the first field
        id1      = row[0]
        owner    = row[1]
        spotid   = row[2]
        cn       = row[4]
        regis    = row[6]
        active   = row[7]
        devtype  = row[8]
        flarmid  = row[9]
        if flarmid == '' or len(flarmid) <9:
           flarmid = getognflarmid(regis)
        if regis == '':
           regis = getognreg(flarmid[3:9])
        idfromdb = getognreg(id1[3:9])
        if spotid != idfromdb:
           print ("Warning reg and name do not match")
        print ("<a> TRKDEV: %-9s %-9s %-7s %-3s  %-3s  %-4s %-9s %-36s "% (id1, idfromdb, regis, cn, active, devtype, flarmid, owner), "</a>", html4%(id1, flarmid,  urllib.parse.quote(owner), active), ">EDIT</a>")

print (html3)
conn.close()
exit(0)
