#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------------------------------------------#
#
#   This script get the data from a directory and extract the FLARM information
#
#-------------------------------------------------------------------------------------------------------------------#
import config
import sys
from dir2filfuncs import dir2fil
pgmver='2.0'
#-------------------------------------------------------------------------------------------------------------------#
#
# arguments:   compid, dayindex, print
#		where compid is the assigned competition ID or 0 for the list of competitions.
#		dayindex is 0 for the first day, 1 second day, etc, ...
#		print is a falg to print the JSON input on pretty print
#-------------------------------------------------------------------------------------------------------------------#
execreq 	= sys.argv[1:]				# -e request
FlarmIDr 	= sys.argv[2:]				# -e request the FlarmID
prtreq 		= sys.argv[3:]				# print request

#FlarmID = str(sys.argv[2:])[2:8].upper()            	# flarm id to scan
#prtreq  = sys.argv[3:]					# print request
SARpath = config.SARpath	                        # directory where to store IGC directory
# directory where will got the IGC files
dirpath = SARpath+"IGCfiles/DIR/"
# directory where will got the IGC files
tmppath = SARpath+"IGCfiles/TMP/"

#
# if we ask to exec the buildIGC

FlarmID = ''
if execreq and execreq[0] == "-e":
    if FlarmIDr:
        FlarmID = FlarmIDr[0].upper()                   # get the FlarmID
        execopt = True

if prtreq and prtreq[0] == "print":                     # if we ask to print
    prt = True
else:
    prt = False



print("\n\nExtract the FLARM infor from the IGC files ",pgmver)
print("================================================\n\n")
print("Usage:   python dir2fil.py -e FLARMID        ")
print("==========================================================\n\n")
print("Args: ", FlarmID,  "From:", dirpath, "To:", tmppath)
dir2fil(FlarmID, prt)
exit(0)
