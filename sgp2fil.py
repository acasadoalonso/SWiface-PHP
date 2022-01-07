#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#
#   This script get the dat from the sgp.aero server and gen the SW JSON file
#
import sys
import json
import datetime
import time
import os
import math
import socket
import config

#-------------------------------------------------------------------------------------------------------------------#
from sgp2filfuncs import sgp2fil

#-------------------------------------------------------------------------------------------------------------------#
#
# arguments:   compid, dayindex, print
#		where compid is the assigned competition ID or 0 for the list of competitions.
#		dayindex is 0 for the first day, 1 second day, etc, ...
#		print is a falg to print the JSON input on pretty print
#

qsgpIDreq 	= sys.argv[1:]				# first arg is the event ID
dayreq 		= sys.argv[2:]				# second arg is the day index within the event
execreq 	= sys.argv[3:]				# -e request
FlarmIDr 	= sys.argv[4:]				# -e request the FlarmID
prtreq 		= sys.argv[5:]				# print request

#

if qsgpIDreq and qsgpIDreq[0] != '0':                   # check the arguments
    qsgpID = sys.argv[1]                                # eventID
    days = str(sys.argv[2])                             # day index within the event
    if days[0].isdigit():
        day = int(days)
        days = ''
    else:
        day = 0
else:
                                                        # assume ZERO and print the all event descriptions
    qsgpID = '0'

                                                        # the FlarmID of the files to be reconstructed
FlarmID = ""
execopt = False
# if we ask to exec the buildIGC
if execreq and execreq[0] == "-e":
    if FlarmIDr:
        FlarmID = FlarmIDr[0].upper()                   # get the FlarmID
        execopt = True

if prtreq and prtreq[0] == "print":                     # if we ask to print
    prt = True
    info= False
elif prtreq and prtreq[0] == "info":                    # if we ask to print
    prt = False
    info= True 
else:
    prt = False
    info= False

sgp2fil(qsgpID,day,FlarmID,execopt,prt)
exit(0)
