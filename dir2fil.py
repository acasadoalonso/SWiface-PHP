#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------------------------------------------#
#
#   This script get the data from a directory and extract the FLARM information
#
#-------------------------------------------------------------------------------------------------------------------#
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import datetime
import time
import os
import math
import pycountry
import socket
from pprint import pprint
from ogndata import *
from getflarm import *
import config
from config import fixcoding

#-------------------------------------------------------------------------------------------------------------------#
#
# arguments:   compid, dayindex, print
#		where compid is the assigned competition ID or 0 for the list of competitions.
#		dayindex is 0 for the first day, 1 second day, etc, ...
#		print is a falg to print the JSON input on pretty print
#-------------------------------------------------------------------------------------------------------------------#

FlarmID = str(sys.argv[1:])[2:8]                        # flarm id to scan
prtreq = sys.argv[2:]					# print request
stats = {}                                              # statistics
SARpath = config.SARpath	                        # directory where to store IGC directory
# directory where will got the IGC files
dirpath = SARpath+"IGCfiles"
# directory where will got the IGC files
tmppath = SARpath+"TMP/"

#

if prtreq and prtreq[0] == "print":                     # if we ask to print
    prt = True
else:
    prt = False

if prtreq and (prtreq[0] == "dir" or prtreq[0] == "DIR"):  # if we ask to directory
    dir = True
    dirpath = sys.argv[3:][0]			        # directory full path
else:
    dir = False


print("\n\nExtract the FLARM infor from the IGC files V1.1 ")
print("================================================\n\n")
print("Usage:   python dir2fil.py FLARMID             or")
print("         python dir2fil.py FLARMID DIR directory-full-path")
print("==========================================================\n\n")
hostname = socket.gethostname()
print("DBhost:", config.DBhost, "ServerName:", hostname)
start_time = time.time()
local_time = datetime.datetime.now()
print("Extracting FLARM info from files at: ", dirpath, ":", FlarmID)
print("==============================================================\n\n")


# check that we have such directory
if not os.path.isdir(dirpath):
    print("Not IGC directory: ", dirpath, "\n\n")
    exit(-1)                                            # nothing else to do
# if the working directory does not exists ??
if not os.path.isdir(tmppath):
    os.system("mkdir "+tmppath)                         # make it !!!
else:
    # remove and clean the working directory
    os.system("rm "+tmppath+"/*")
ld = os.listdir(dirpath)                                # get the list of files
# count of number of records processed
cnt = 0
for f in ld:                                            # scan all the files on the from directory
    fd = open(dirpath+"/"+f, 'r')                       # open the file
    # extract the FLARM data from the embeded records
    cnt += getflarmfile(fd, f, tmppath+f, stats, prt)
    fd.close()                                          # close the file
    sys.stdout.flush()                                  # print results
print("Records processed:", cnt, "\n\nStats & Warnings:", stats)     # print the stats
if FlarmID == '' or FlarmID == 'NFLARM':                # if no FlarmID, nothing else to do
    print("Files processed now at:", tmppath, "\n")
    print("==============================================================\n\n")
    exit()                                              # nothing else to do ...
# remember the current directory
cwd = os.getcwd()
print("From CD:", cwd, "To:", tmppath)                  # report it
# report current directory and the new one
os.chdir(tmppath)
# file name of the rebuilt file
fname = FlarmID+'.'+getognreg(FlarmID)+'.'+getogncn(FlarmID)+'.igc'
if os.path.isfile(fname):                               # remove to avoid errors
    os.remove(fname)                                    # remove if exists
    # get the new IGC files based on the FLARM messages
os.system('grep "FLARM "'+FlarmID+' * | sort -k 3 | python ' +
          cwd+'/genIGC.py '+FlarmID+' > '+fname)

print("New IGC rebuilt file:", fname, " is at:", tmppath)
print("==============================================================\n\n")
