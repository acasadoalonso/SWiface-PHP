#!/usr/bin/python
# -*- coding: UTF-8 -*-

#
#   This script get the dat from a directory and extract the FLARM information
#
import sys
import json
import urllib2
import datetime
import time
import os
import math
import pycountry
import socket
from  pprint    import pprint
from  ogndata   import *
from  getflarm  import *


#-------------------------------------------------------------------------------------------------------------------#
import config
from config import fixcoding
	
#-------------------------------------------------------------------------------------------------------------------#
#
# arguments:   compid, dayindex, print
#		where compid is the assigned competition ID or 0 for the list of competitions.
#		dayindex is 0 for the first day, 1 second day, etc, ...
#		print is a falg to print the JSON input on pretty print
#

FlarmID=str(sys.argv[1:])[2:8]
prtreq   =sys.argv[2:]					# print request
 
stats={}                                                # statistics 

cucpath=config.cucFileLocation				# directory where to stor the JSON file generated
DBpath=config.DBpath		        		# directory where to stor IGC files
dirpath=DBpath+"IGCfiles"                               # directory where will got the IGC files

#

if prtreq and prtreq[0]=="print":                       # if we ask to print
	prt=True
else:
	prt=False
 
print "\n\nExtract the FLARM infor from the IGC files V1.0 "
print "================================================\n\n"
print "Usage python dir2fil.py FLARMID"
print "===============================\n\n"
hostname=socket.gethostname()
print "DBhost:", config.DBhost, "ServerName:", hostname
start_time = time.time()
local_time = datetime.datetime.now()
print "================================================\n\n"


if not os.path.isdir(dirpath):                          # check that we have such directory
    print "Not IGC directory\n\n"
    exit(-1)
os.system("rm "+DBpath+"/TMP/*")                        # remove and clean the working directory 
ld = os.listdir(dirpath)                                # get the list of files 
cnt = 0                                                 # count of number of records processed
for f in ld:                                            # scan all the files on the from directory
    fd=open(dirpath+"/"+f, 'r')                         # open the file
    cnt +=getflarmfile(fd, f, DBpath+"/TMP/"+f, stats)  # extract the FLARM data from the embeded records
    fd.close()                                          # close the file
print "From CD:", os.getcwd(), "To:", DBpath+"/TMP/"
os.chdir(DBpath+"/TMP/")                                # report current directory and the new one
fname=FlarmID+'.'+getognreg(FlarmID)+'.'+getogncn(FlarmID)+'.igc'
if os.path.isfile(fname):                               # remove to avoid errors
    os.remove(fname)                                    # remove if exists
                                                        # get the new IGC files based on the FLARM messages
os.system('grep "FLARM "'+FlarmID+' * | sort -k 3 | python /var/www/html/SWS/genIGC.py '+FlarmID+' > '+fname)

print "Records processed:",cnt, "\n\nStats:", stats



