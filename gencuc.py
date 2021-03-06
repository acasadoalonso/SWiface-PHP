#!/usr/bin/python

#
#   This script looks into the SWiface database and generates a pseudo .CUC file
#
import config
if config.MySQL:
    import MySQLdb
else:
    import sqlite3
import datetime
import time
import sys
import os
import kpilot
import kglider

ipaddr = sys.argv[1:]
dbpath = config.DBpath
pwd = os.environ['PWD']
cucpath = pwd+"/cuc/"
if ipaddr:
    user = sys.argv[1]
else:
    user = os.environ['USER']

if (config.MySQL):
    print("Generate live .CUC files V1.2 from  MySQL DB:", config.DBname, "at", config.DBhost)
else:
    print("Generate live .CUC files V1.2 from  " + \
        dbpath + "SWIface.db the GLIDERS table")
start_time = time.time()
local_time = datetime.datetime.now()
print("Time is now:", local_time)				# print the time for information only
fl_date_time = local_time.strftime("%Y%m%d")			# get the local time
CUC_DATA = cucpath + "LIVE" + fl_date_time + \
    '.cuc'		# name of the CUC to be generated
print("CUC data file is: ", CUC_DATA, " User:", user)		# just a trace
datafile = open(CUC_DATA, 'w')					# open the output file
cuchdr = open(cucpath + "LIVEhdr.txt", 'r')			# opend the header file
cuctail = open(cucpath + "LIVEtail.txt", 'r')			# open the trailer file
buf = cuchdr.read()						# start reading the header file
datafile.write(buf)						# copy into the output file

#
if (config.MySQL):
    conn = MySQLdb.connect(host=config.DBhost, user=config.DBuser,
                           passwd=config.DBpasswd, db=config.DBname)     # connect with the database
else:
    filename = dbpath+'SWiface.db'				# open th DB in read only mode
    fd = os.open(filename, os.O_RDONLY)
    conn = sqlite3.connect('/dev/fd/%d' % fd)
cursD = conn.cursor()						# cursor for the ogndata table
cursG = conn.cursor()						# cursor for the glider table
pn = 0								# number of pilots found
en = 0								# number of pilots found
# get all the glifers flying now
cursD.execute('select distinct idflarm from OGNDATA')
for row in cursD.fetchall():					# search all the rows
    idflarm = row[0]						# flarmid is the first field
    idf = idflarm[3:9]						# we skip the first 3 chars
    if kglider.kglid and idflarm not in kglider.kglider:
        continue
    # search now into the gliding database
    sqlcmd = "select registration, cn, type from GLIDERS where idglider = '%s';" % idf
    cursG.execute(sqlcmd)
    gli = cursG.fetchone()					# get the data from the DB
    if gli and gli != None:					# did we find it ??? Index is unique, only one row
        regi = gli[0]					# get the registration
        cn = gli[1]					# get the competition numbers
        if cn == "" or cn == " ":
            cn = regi[4:6]                            # if none ?
        type = gli[2]					# get glider type
    else:
        regi = 'NO-NAME'
        cn = str(pn)
        type = 'NOTYPE'
    if idflarm in kpilot.kpilot:				# check if know the pilot because is our database kpilot.py
        # in that case place the name of the pilot
        pname = kpilot.kpilot[idflarm]
    else:
        if regi == 'NO-NAME':
            pname = "Pilot NN-"+str(pn)			# otherwise just say: NoName#
        else:
            pname = regi					# use the registration as pilot name
#   								write the Pilot detail
#   "Tpilot","",*0,"FLRDDE1FC","Ventus","EC-TTT","TT","",0,"",0,"",1,"",""		# the template to use
    pn += 1
    buf = '"' + pname + '","",*0,"' + idflarm + '","' + type + '","' + regi + \
        '","' + cn + '","",0,"",0,"",1,"",""\n' 	# write tha into the psuedo CUC file
    if (regi == "NO-NAME" and en > 0):
        continue
    print("D==>: ", idflarm, pname, regi, cn, type)
    if regi[0] == 'F' and en > 0:
        continue
    en += 1							# entry number
    # write the pilot information into the pseudo CUC file
    datafile.write(buf)

# write the day entry

# [Starts]							# this is the template
#
# [Day_02/03/2016]
# D02032016-010400000

datafile.write("[Starts]\n")					# write it in the output file
datafile.write(" \n")
buf = "[Day_"+local_time.strftime("%d/%m/%Y")+"]\n"
datafile.write(buf)
buf = "D" + local_time.strftime("%d%m%Y") + "-010400000\n"
datafile.write(buf)

# wite the trailer in order to complete the format of the .CUC file

buf = cuctail.read()						# read the trailer file
datafile.write(buf)						# write it into the output file
#
# close the files and exit
#

datafile.close()
cuchdr.close()
cuctail.close()
conn.commit()
conn.close()
if not config.MySQL:
    os.close(fd)
if pn == 0:
    print("No pilots found ... CUC invalid")
    print("===============================")
    exit(-1)
else:
    print("Pilots found ... ", pn, en)
    print("===========================")
    exit(0)
