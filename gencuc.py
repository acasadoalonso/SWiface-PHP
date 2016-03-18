#!/usr/bin/python 

#
#   This script looks into the SWiface database and generates a pseudo .CUC file
#


import sqlite3
import datetime
import time
import sys
import os
import kpilot

dbpath ="/nfs/OGN/SWdata/"
pwd=os.environ['PWD']
cucpath=pwd+"/cuc/"
run=os.environ['APACHE_RUN_USER']

print "Generate live .CUC files V1.1 from  " +dbpath+ "SWIface.db the GLIDERS table"
start_time = time.time()
local_time = datetime.datetime.now()
print "Time is now:", local_time				# print the time for information only
fl_date_time = local_time.strftime("%Y%m%d")			# get the local time
CUC_DATA = cucpath + "LIVE" + fl_date_time+'.cuc'		# name of the CUC to be generated
print "CUC data file is: ", CUC_DATA, " User:", run		# just a trace
datafile = open (CUC_DATA, 'w')					# open the output file
cuchdr   = open (cucpath + "LIVEhdr.txt", 'r')			# opend the header file
cuctail  = open (cucpath + "LIVEtail.txt", 'r')			# open the trailer file
buf=cuchdr.read()						# start reading the header file
datafile.write(buf)						# copy into the output file
# 
filename=dbpath+'SWiface.db'					# open th DB in read only mode
fd = os.open(filename, os.O_RDONLY)
conn = sqlite3.connect('/dev/fd/%d' % fd)
cursD=conn.cursor()						# cursor for the ogndata table
cursG=conn.cursor()						# cursor for the glider table
pn=0								# number of pilots found
cursD.execute('select distinct idflarm from OGNDATA')		# get all the glifers flying now 
for row in cursD.fetchall():					# search all the rows
    idflarm=row[0]						# flarmid is the first field
    idf=idflarm[3:9]						# we skip the first 3 chars      
    cursG.execute("select registration, cn, type from GLIDERS where idglider = ?", [idf])		# search now into the gliding database
    gli=cursG.fetchone()					# get the data from the DB
    if gli and gli != None:					# did we find it ??? Index is unique, only one row
                regi=gli[0]					# get the registration 
                cn=gli[1]					# get the competition numbers
		if cn == "":
			cn="XX"					# if none ?
                type=gli[2]					# get glider type
    else:
                regi='NO-NAME'
                cn='NN'
                type='NOTYPE'
    if idflarm in kpilot.kpilot:				# check if know the pilot because is our database kpilot.py
	pname=kpilot.kpilot[idflarm]				# in that case place the name of the pilot
    else:
	pname="Pilot NN-"+str(pn)				# otherwise just say: NoName#
    print "D==>: ", idflarm, pname, regi, cn, type
#   								write the Pilot detail
#   "Tpilot","",*0,"FLRDDE1FC","Ventus","EC-TTT","TT","",0,"",0,"",1,"",""		# the template to use
    pn +=1 
    buf='"' +pname+ '","",*0,"' +idflarm+ '","' +type+ '","' +regi+ '","' +cn+ '","",0,"",0,"",1,"",""\n' 	# write tha into the psuedo CUC file
    datafile.write(buf)						# write the pilot information into the pseudo CUC file
    
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
cuchdr.close()
cuctail.close()
conn.commit()
conn.close()
os.close(fd)
if pn == 0:
	print "No pilots found ... CUC invalid"
	print "==============================="
	exit(-1)
else:
	print "Pilots found ... ", pn
	print "======================"
	exit(0)
