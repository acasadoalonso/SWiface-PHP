#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#
#   This script get the dat from the sgp.aero server and gen the extracted IGC file form the info contained on the Flarm LL records
#
import sys
import config						# config.py generated by the genconfig.py script

#-------------------------------------------------------------------------------------------------------------------#
from sgp2filfuncs import sgp2fil			# the extractor

#-------------------------------------------------------------------------------------------------------------------#
#
# arguments:   compid, dayindex, -e,  FlarmID, print
# ==================================================
#
#		where compid is the assigned competition ID or 0 for the list of competitions.
#		dayindex is 0 for the first day, 1 second day, etc, ...
#		-e is to request the exec option and gen the IGC file
#		FlarmID is the FlarmID that we are looking for
#		print is a flag to print the JSON input on pretty print
#

qsgpIDreq 	= sys.argv[1:]				# first arg is the event ID
dayreq 		= sys.argv[2:]				# second arg is the day index within the event
execreq 	= sys.argv[3:]				# -e request
FlarmIDr 	= sys.argv[4:]				# the FlarmID
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
prt=False
# if we ask to exec the buildIGC
if execreq and execreq[0] == "-e":
    if FlarmIDr:
        FlarmID = FlarmIDr[0].upper()                   # get the FlarmID
        if len(FlarmID) == 9:				# in case of ICAxxxxxx
           FlarmID = FlarmID[3:9]
        execopt = True

if prtreq and prtreq[0] == "print":                     # if we ask to print
    prt = True
else:
    prt = False

sgp2fil(qsgpID,day,FlarmID,execopt,prt)			# invoke the extractor
exit(0)

