#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#
#   This script get the dat from the sgp.aero server and gen the SW JSON file
#
import sys
import json
import urllib.request, urllib.error, urllib.parse
import datetime
import time
import os
import math
import pycountry
import socket
from pprint import pprint
from ognddbfuncs import *
from getflarm import *


#-------------------------------------------------------------------------------------------------------------------#
import config

#-------------------------------------------------------------------------------------------------------------------#
#
# arguments:   compid, dayindex, print
#		where compid is the assigned competition ID or 0 for the list of competitions.
#		dayindex is 0 for the first day, 1 second day, etc, ...
#		print is a falg to print the JSON input on pretty print
#

qsgpIDreq = sys.argv[1:]				# first arg is the event ID
dayreq = sys.argv[2:]					# second arg is the day index within the event
execreq = sys.argv[3:]					# -e request
FlarmIDr = sys.argv[4:]					# -e request the FlarmID
prtreq = sys.argv[5:]					# print request

stats = {}                                              # statistics

# directory where to stor the JSON file generated
cucpath = config.cucFileLocation
SARpath = config.SARpath                		# directory where to stor IGC files
                                                        # table with the pilots ID and namme
pilotsID = {}
                                                        # table with the pilots ID and namme
flarmsID = {}
                                                        # directory where will got the IGC files
dirpath = SARpath+"SGP"


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
        FlarmID = FlarmIDr[0]                           # get the FlarmID
        execopt = True

if prtreq and prtreq[0] == "print":                     # if we ask to print
    prt = True
else:
    prt = False

print("\n\nExtract the IGC files from the www.sgp.aero web server V1.2")
print("Usage:      python sgp2fil.py COMPID indexday -e FlarmID print\n\n")
print("==============================================================\n\n")
hostname = socket.gethostname()
print("DBhost:", config.DBhost, "ServerName:", hostname)
start_time = time.time()
local_time = datetime.datetime.now()
# get the data from the server
j = urllib.request.urlopen('http://www.crosscountry.aero/c/sgp/rest/comps/')
j_obj = json.load(j)                                    # convert it
if qsgpID == '0':                                       # just display the list of competition and exit
    #print j_obj
    j = json.dumps(j_obj, indent=4)
    print(j)
    exit(0)                                             # nothing else to do it
else:
    for xx in j_obj:                                    # extract the data of our event
        if xx['id'] == int(qsgpID):
            print("Title:", xx['fullEditionTitle'])

                                                        # print the time for information only
    print("CompID:", qsgpID, "Time is now:", local_time)

fl_date_time = local_time.strftime("%Y%m%d")            # get the local time
print("===========================: \n") 		# just a trace

#
# get the JSON string for the web server
#
j = urllib.request.urlopen( 'http://www.crosscountry.aero/c/sgp/rest/comp/'+str(qsgpID))
j_obj = json.load(j)                                    # convert it to dict
if prt:
    #print j_obj
    j = json.dumps(j_obj, indent=4)
    print(j)
    # exit(0)
#
# the different pieces of information
#

npil = 0						# number of pilots found
pilots = j_obj["p"]					# get the pilot information
print("Pilots:", len(pilots))
print("==========")
for id in pilots:                                       # disply the pilot information for better doc
    #
    print("---------------------")
    pid = pilots[id]["i"]                               # get the pilot ID
    fname = pilots[id]["f"]                             # first name
    lname = pilots[id]["l"]                             # last name
    compid = pilots[id]["d"]                            # competition number
    country = pilots[id]["z"]                           # two letters country code
    model = pilots[id]["s"]                             # aircraft model
    j = pilots[id]["j"]                                 # ranking list
    rankingid = pilots[id]["r"]                         # ranking id
    flarmID = pilots[id]["q"]                           # FlarmID
    registration = pilots[id]["w"]                      # registration
    if flarmID == "":
                                                        # get it from the OGN data
        flarmID = getognflarmid(registration)

    if hostname == "SWserver":			        # deal with the different implementation of pycountry
                                                        # the the 3 letter country code
        ccc = pycountry.countries.get(alpha_2=country)
        country = ccc.alpha_3			        # convert to a 3 letter code
    else:
                                                        # the the 3 letter country code
        ccc = pycountry.countries.get(alpha_2=country)
        country = ccc.alpha_3			        # convert to a 3 letter code

    pilotname = (fname+" "+lname).encode('utf8').decode('utf-8')
    print("Pilot:", pid, pilotname, compid, country, model, j, rankingid, registration, flarmID)
    pilotsID[pid] = pilotname
    flarmsID[pid] = flarmID
    npil += 1					        # increase the number of pilots
    print("---------------------")

print("Competition")
print("===========")
comp = j_obj["c"]					# get the competition information
comp_firstday = comp['a']			        # first day of the competition
comp_lastday = comp['b']			        # last day of the competition
comp_name = comp['t']			                # event name
comp_shortname = comp['l']			        # event short name
comp_id = comp['i']
print("Comp ID:", comp_id, "Name:", comp_name, "Short name:", comp_shortname, comp_firstday, comp_lastday)
numberofactivedays = 0

if j_obj.get("j") != None:
    numberofactivedays = j_obj["j"]
if j_obj.get("i") == None:			        # check if is fully setup the web site
    print("No index of days ... exiting.")
    exit(-1)
indexofdays = j_obj["i"]
                                                        #print "Index of Days", indexofdays
if days != '':                                          # check the days
    cday = 0
    for dayday in indexofdays:
        #print "DAYDAY", days, dayday
        if dayday["l"].upper() == days.upper():
            day = cday
            break
        else:
            cday += 1
            continue

date = indexofdays[day]["d"]		                # date
title = indexofdays[day]["t"] 		                # day tittle
shorttitle = indexofdays[day]["l"]    	                # day short title
starttime = indexofdays[day]["a"]    	                # start time millis from midnite
daytype = indexofdays[day]["y"]    	                # day type: 1, 2, 3 ...
dayid = indexofdays[day]["i"] 		                # day ID
print("DATE:", date, "Title:", title, "Day:", shorttitle, "==>", day, "\nStart time(millis):", starttime, "Day type:", daytype, "Day ID:", dayid, "Number of active days:", numberofactivedays)
                                                        # get the data for day
d = urllib.request.urlopen(
    'http://www.crosscountry.aero/c/sgp/rest/day/'+str(qsgpID)+'/'+str(dayid))
d_obj = json.load(d)                                    # convert to dict
race = d_obj["l"]				        # get the race information
results = d_obj["r"]			        	# get the results information
print("Race:", race)                                    # show the race name
print("Results:")
print("========")
#pprint (results)
                                                        # get the scoring info
rr = results['s']
# pprint(rr)
p = 0                                                   # number of pilots
if os.path.isdir(dirpath+"/"+str(date)):
                                                        # delete all the files on that directory
    os.system("rm "+dirpath+"/"+str(date)+"/*")
for r in rr:                                            # get all the pilots
    # pprint(r)
    pilotid = r['h']                                    # pilot ID
    cn = r['j']                                         # competition id
    if 'g' in r:
        fr = r['g']                                     # flight recorder used
    else:
        fr = "ZZZ"
        print("No FR>>>>:", pilotid, cn)
                                                        # file number of the web server
    filenum = r['w']
    if filenum == 0:
        print("Error: IGC file not found !!!>>> PID", pilotid, "Pilot: ", str(pilotsID[pilotid]).encode('utf-8').decode('utf-8'), cn, filenum)
        continue
    fftc = "http://www.crosscountry.aero/flight/download/sgp/" + \
        str(filenum)                                    # the URL to download the IGC fle
    print("Pilot: ", str(pilotsID[pilotid]).encode('utf-8').decode('utf-8'), cn, filenum, "FR:", fr, "FlarmID:", flarmsID[pilotid])
    if not os.path.isdir(dirpath+"/"+str(date)):
        os.system("mkdir "+dirpath+"/"+str(date))
        os.system("chmod 775 "+dirpath+"/"+str(date))
        print(" OK directory made")

    req = urllib.request.Request(fftc)
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/text")
    fd = urllib.request.urlopen(req)                    # open the url resource
                                                        # call the routine that will read the file and handle the FLARM records
    igcfilename = dirpath+"/"+str(date)+"/"+cn+"."+fr[4:7]+".igc"
                                                        # grab and convert FLARM records
    cnt = getflarmfile(fd, cn, igcfilename,  stats, prt)
    sys.stdout.flush()                                  # print results
    if prt:
        print("Number of records:", igcfilename, cnt)
    print("----------------------------------------------------------------")
    p += 1                                              # counter of pilotsa
if p != npil:
    print("Error on geting the score data ....Pilots:", npil, "Files:", p, "\n\n")

print(stats)


                                                        # print the number of pilots as a reference and control
print("= Pilots ===========================", npil)

                                                        # print information about the day
d = urllib.request.urlopen('http://www.crosscountry.aero/c/sgp/rest/day/'+str(qsgpID)+'/'+str(dayid))
d_obj = json.load(d)
if prt:
    print("____________________________________________________________")
    d = json.dumps(d_obj, indent=4)
    print(d)
if numberofactivedays == 0:
    print("No active days ...")

print("=============================")
print("Day: ", day, "DayID: ", dayid)
print("=============================")
#print "DDD", d_obj
comp_day = d_obj["@type"]
comp_id = d_obj["e"]				        # again the compatition ID
comp_dayid = d_obj["i"]				        # the day ID
comp_date = d_obj["d"]				        # date in milliseconds from the Unix epoch
# day type: 1= valid, 2= practice, 3= canceled, 4= rest, 9= other
comp_daytype = d_obj["y"]
comp_daytitle = d_obj["l"]				# day title
comp_shortdaytitle = d_obj["t"]				# short day title
comp_starttime = d_obj["a"]				# start time millis from midnite
comp_startaltitude = d_obj["h"]				# start altitude
comp_finishaltitude = d_obj["f"]			# finish altitude
print("Comp day:", comp_day, "Comp ID:", comp_id, "Comp ID DAY:", comp_dayid, date, "Title:", comp_daytitle, comp_shortdaytitle, "\nStart time (millis):", comp_starttime, "Start alt.:", comp_startaltitude, "Finish Alt.:", comp_finishaltitude)
if "k" in d_obj:
    comp_taskinfo = d_obj["k"]			        # task infor data
else:
    print("No task for that day...")
    print("WARNING: No valid JSON file generated .....................")
    exit()
# event

#
# close the files and exit
#
if execopt:
    cwd = os.getcwd()
    print("Extracting the IGC file from embeded FLARM messages \nFrom CD:", cwd, "To:", dirpath + \
        "/"+str(date))
                                                        # report current directory and the new one
    os.chdir(dirpath+"/"+str(date))

    fname = FlarmID+'.'+getognreg(FlarmID)+'.'+getogncn(FlarmID)+'.igc'
                                                        # remove to avoid errors
    if os.path.isfile(fname):
                                                        # remove if exists
        os.remove(fname)
                                                        # get the new IGC files based on the FLARM messages
    os.system('grep "FLARM "'+FlarmID+' * | sort -k 3 | python ' +
              cwd+'/genIGC.py '+FlarmID+' > '+fname)
    print("Resulting IGC file is on:", dirpath+"/"+str(date), "As: ", fname)

if npil == 0:
    exit(-1)
else:
    print("Pilots found ... ", npil)
    print("=====================================================================: \n\n\n") 		# just a trace
    exit(0)
