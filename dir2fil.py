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
#-------------------------------------------------------------------------------------------------------------------#

FlarmID=str(sys.argv[1:])[2:8]                          # flarm id to scan
prtreq   =sys.argv[2:]					# print request
stats={}                                                # statistics 
SARpath=config.SARpath	                		# directory where to store IGC directory 
dirpath=SARpath+"IGCfiles"                              # directory where will got the IGC files
tmppath=SARpath+"TMP/"                                  # directory where will got the IGC files

#

if prtreq and prtreq[0]=="print":                       # if we ask to print
	prt=True
else:
	prt=False

if prtreq and (prtreq[0]=="dir" or prtreq[0] == "DIR"): # if we ask to directory
	dir=True
        dirpath   =sys.argv[3:][0]			# directory full path
else:
	dir=False

 
print "\n\nExtract the FLARM infor from the IGC files V1.1 "
print "================================================\n\n"
print "Usage:   python dir2fil.py FLARMID             or"
print "         python dir2fil.py FLARMID DIR directory-full-path"
print "==========================================================\n\n"
hostname=socket.gethostname()
print "DBhost:", config.DBhost, "ServerName:", hostname
start_time = time.time()
local_time = datetime.datetime.now()
print "Extracting FLARM info from files at: ", dirpath, FlarmID
print "==============================================================\n\n"


if not os.path.isdir(dirpath):                          # check that we have such directory
    print "Not IGC directory: ", dirpath, "\n\n"
    exit(-1)                                            # nothing else to do 
if not os.path.isdir(tmppath):                          # if the working directory does not exists ??
    os.system ("mkdir "+tmppath)                        # make it !!!
else:
    os.system("rm "+tmppath+"/*")                       # remove and clean the working directory 
ld = os.listdir(dirpath)                                # get the list of files 
cnt = 0                                                 # count of number of records processed
for f in ld:                                            # scan all the files on the from directory
    fd=open(dirpath+"/"+f, 'r')                         # open the file
    cnt +=getflarmfile(fd, f, tmppath+f, stats, prt)    # extract the FLARM data from the embeded records
    fd.close()                                          # close the file
print "Records processed:",cnt, "\n\nStats:", stats     # print the stats
if FlarmID == '':                                       # if no FlarmID, nothing else to do 
        print "Files processed now at:", tmppath, "\n"
        print "==============================================================\n\n"
        exit()                                          # nothing else to do ...
cwd=os.getcwd()                                         # remember the current directory
print "From CD:", cwd, "To:", tmppath                   # report it
os.chdir(tmppath)                                       # report current directory and the new one
fname=FlarmID+'.'+getognreg(FlarmID)+'.'+getogncn(FlarmID)+'.igc'   # file name of the rebuilt file
if os.path.isfile(fname):                               # remove to avoid errors
    os.remove(fname)                                    # remove if exists
                                                        # get the new IGC files based on the FLARM messages
os.system('grep "FLARM "'+FlarmID+' * | sort -k 3 | python '+cwd+'/genIGC.py '+FlarmID+' > '+fname)

print "New IGC rebuilt file:", fname, " is at:", tmppath
print "==============================================================\n\n"



