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
print "Usage python dir2fil.py FLARMID  "
hostname=socket.gethostname()
print "DBhost:", config.DBhost, "ServerName:", hostname
start_time = time.time()
local_time = datetime.datetime.now()
print "=================================: \n" 		# just a trace


if not os.path.isdir(dirpath):                          # check that we have such directory
    print "Not IGC directory\n\n"
    exit(-1)
ld = os.listdir(dirpath)                                # get the list of files 
cnt = 0                                                 # count of number of records processed
for f in ld:
    fd=open(dirpath+"/"+f, 'r')                         # open the file
    cnt +=getflarmfile(fd, f, DBpath+"/TMP/"+f, stats)  # extract the FLARM data from the embeded records
    fd.close()                                          # close the file
print "From CD:", os.getcwd(), "To:", os.chdir(DBpath+"/TMP/") # report current directory and the new one

if os.path.isfile(FlarmID+'.igc'):                      # remove to avoid errors
    os.remove(FlarmID+'.igc')                           # remove if exists
                                                        # get the new IGC files based on the FLARM messages
os.system('grep "FLARM "'+FlarmID+' * | sort -k 3 | python /var/www/html/SWS/genIGC.py '+FlarmID+' > '+FlarmID+'.igc')

print "Records processed:",cnt, "\n\nStats:", stats



