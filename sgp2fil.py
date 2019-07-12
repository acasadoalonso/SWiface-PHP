#!/usr/bin/python
# -*- coding: UTF-8 -*-

#
#   This script get the dat from the sgp.aero server and gen the SW JSON file
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

qsgpIDreq=sys.argv[1:]					# first arg is the event ID
dayreq   =sys.argv[2:]					# second arg is the day index within the event
execreq  =sys.argv[3:]					# -e request
FlarmIDr =sys.argv[4:]					# -e request the FlarmID
prtreq   =sys.argv[5:]					# print request
 
stats={}                                                # statistics 

cucpath=config.cucFileLocation				# directory where to stor the JSON file generated
SARpath=config.SARpath		        		# directory where to stor IGC files
pilotsID={}                                             # table with the pilots ID and namme
flarmsID={}                                             # table with the pilots ID and namme
dirpath=SARpath+"SGP"                                   # directory where will got the IGC files


#

if qsgpIDreq and qsgpIDreq[0] != '0':                   # check the arguments
	qsgpID   =        sys.argv[1]                   # eventID
	days     =        str(sys.argv[2])              # day index within the event
	if days[0].isdigit():	
		day =     int(days)
		days=''
	else:
		day=0
else:
	qsgpID='0'                                      # assume ZERO and print the all event descriptions

FlarmID=""                                              # the FlarmID of the files to be reconstructed
execopt=False
if execreq and execreq[0]=="-e":                        # if we ask to exec the buildIGC
    if FlarmIDr:
        FlarmID=FlarmIDr[0]                             # get the FlarmID
        execopt=True

if prtreq and prtreq[0]=="print":                       # if we ask to print
	prt=True
else:
	prt=False
 
print "\n\nExtract the IGC files V1.1 from  the www.sgp.aero web server"
print "Usage:      python sgp2fil.py COMPID indexday -e FlarmID print\n\n"
print "==============================================================\n\n"
hostname=socket.gethostname()
print "DBhost:", config.DBhost, "ServerName:", hostname
start_time = time.time()
local_time = datetime.datetime.now()
j = urllib2.urlopen('http://www.crosscountry.aero/c/sgp/rest/comps/')   # get the data from the server
j_obj = json.load(j)                                    # convert it
if qsgpID == '0':                                       # just display the list of competition and exit
	#print j_obj
	j=json.dumps(j_obj, indent=4)
	print j
	exit(0)                                         # nothing else to do it
else:
	for xx in j_obj:                                # extract the data of our event
		if xx['id'] == int(qsgpID):
			print "Title:", xx['fullEditionTitle']
	print "CompID:", qsgpID, "Time is now:", local_time     # print the time for information only

fl_date_time = local_time.strftime("%Y%m%d")            # get the local time
print "===========================: \n" 		# just a trace

#
# get the JSON string for the web server
#
j = urllib2.urlopen('http://www.crosscountry.aero/c/sgp/rest/comp/'+str(qsgpID))
j_obj = json.load(j)                                    # convert it to dict
if prt:
	#print j_obj
	j=json.dumps(j_obj, indent=4)
	print j
        #exit(0)
#
# the different pieces of information
#

npil=0							# number of pilots found
pilots=j_obj["p"]					# get the pilot information
print "Pilots:", len(pilots)
print "=========="
for id in pilots:                                       # disply the pilot information for better doc
#
        print "---------------------"
	pid= 		pilots[id]["i"] 		# get the pilot ID   
	fname= 		pilots[id]["f"]			# first name    
	lname= 		pilots[id]["l"] 		# last name   
	compid= 	pilots[id]["d"]			# competition number    
	country= 	pilots[id]["z"] 		# two letters country code   
	model= 		pilots[id]["s"]			# aircraft model    
	j= 		pilots[id]["j"]    		# ranking list
	rankingid= 	pilots[id]["r"]			# ranking id
	flarmID= 	pilots[id]["q"]			# FlarmID
	registration= 	pilots[id]["w"]			# registration
        if flarmID =="":
            flarmID=getognflarmid(registration)         # get it from the OGN data

	if hostname == "SWserver":			# deal with the different implementation of pycountry
		ccc = pycountry.countries.get(alpha_2=country)	# the the 3 letter country code
    		country=ccc.alpha_3			# convert to a 3 letter code
	else:
		ccc = pycountry.countries.get(alpha_2=country)	# the the 3 letter country code
    		country=ccc.alpha_3			# convert to a 3 letter code

	pilotname=fixcoding(fname+" "+lname).encode('utf8')
        print "Pilot:", pid, pilotname, compid, country, model, j, rankingid, registration, flarmID
        pilotsID[pid]=pilotname
        flarmsID[pid]=flarmID
	npil += 1					# increase the number of pilots
        print "---------------------"

print "Competition"
print "==========="
comp=j_obj["c"]						# get the competition information
comp_firstday		=comp['a']			# first day of the competition
comp_lastday		=comp['b']			# last day of the competition
comp_name		=comp['t']			# event name
comp_shortname		=comp['l']			# event short name
comp_id			=comp['i']
print "Comp ID:", comp_id, "Name:", comp_name, "Short name:", comp_shortname, comp_firstday, comp_lastday
numberofactivedays	= 0

if 	j_obj.get ("j") != None :
	numberofactivedays	=j_obj["j"]
if 	j_obj.get ("i") == None :			# check if is fully setup the web site
	print "No index of days ... exiting."
	exit(-1)
indexofdays		=j_obj["i"]
#print "Index of Days", indexofdays
if days != '':                                          # check the days
	cday=0 
	for dayday in indexofdays:
		#print "DAYDAY", days, dayday
		if dayday["l"].upper() == days.upper():
			day = cday
			break
		else:
			cday += 1
			continue
	
date			=indexofdays[day]["d"]		# date    
title			=indexofdays[day]["t"] 		# day tittle   
shorttitle		=indexofdays[day]["l"]    	# day short title
starttime		=indexofdays[day]["a"]    	# start time millis from midnite
daytype			=indexofdays[day]["y"]    	# day type: 1, 2, 3 ...
dayid			=indexofdays[day]["i"] 		# day ID 
print "DATE:", date, "Title:", title, "Day:", shorttitle,"==>", day, "\nStart time(millis):", starttime, "Day type:", daytype, "Day ID:", dayid, "Number of active days:", numberofactivedays
                                                        # get the data for day 
d = urllib2.urlopen('http://www.crosscountry.aero/c/sgp/rest/day/'+str(qsgpID)+'/'+str(dayid))
d_obj = json.load(d)                                    # convert to dict
race=d_obj["l"]					        # get the race information
results=d_obj["r"]			        	# get the results information
print "Race:", race                                     # show the race name
print "Results:"
print "========"
#pprint (results)
rr=results['s']                                         # get the scoring info
#pprint(rr)
p=0                                                     # number of pilots
os.system("rm "+dirpath+"/DAY"+str(day)+"/*")           # delete all the files on that directory 
for r in rr:                                            # get all the pilots
    #pprint(r)
    pilotid         =r['h']                             # pilot ID
    cn              =r['j']                             # competition id
    if 'g' in r:
        fr          =r['g']                             # flight recorder used
    else:
        fr="ZZZ"
        print "No FR>>>>:", pilotid, cn
    filenum         =r['w']                             # file number of the web server
    if filenum == 0:
        print "Error: IGC file not found !!!>>> PID", pilotid, "Pilot: ", fixcoding(pilotsID[pilotid]), cn, filenum
        continue
    fftc="http://www.crosscountry.aero/flight/download/sgp/"+str(filenum)   # the URL to download the IGC fle
    print "Pilot: ", fixcoding(pilotsID[pilotid]), cn, filenum, "FR:", fr, "FlarmID:", flarmsID[pilotid]
    if not os.path.isdir(dirpath+"/DAY"+str(day)):
                    os.system("mkdir "+dirpath+"/DAY"+str(day))
                    print " OK directory made"

    req = urllib2.Request(fftc)
    req.add_header("Accept","application/json")
    req.add_header("Content-Type","application/text")
    fd = urllib2.urlopen(req)                           # open the url resource
                                                        # call the routine that will read the file and handle the FLARM records
    igcfilename=dirpath+"/DAY"+str(day)+"/"+cn+"."+fr[4:7]+".igc"
    cnt=getflarmfile(fd, cn, igcfilename,  stats, prt)
    if prt:
       print "Number of records:", igcfilename, cnt
    print "----------------------------------------------------------------"
    p +=1                                               # counter of pilotsa
if p != npil:
    print "Error on geting the score data ....Pilots:", npil, "Files:", p, "\n\n"

print stats


print "= Pilots ===========================", npil      # print the number of pilots as a reference and control

# print information about the day
d = urllib2.urlopen('http://www.crosscountry.aero/c/sgp/rest/day/'+str(qsgpID)+'/'+str(dayid))
d_obj = json.load(d)
if prt:
	print "____________________________________________________________"
	d=json.dumps(d_obj, indent=4)
	print d
if numberofactivedays == 0:
	print "No active days ..."

print "============================="
print "Day: ", day, "DayID: ", dayid
print "============================="
#print "DDD", d_obj
comp_day		=d_obj["@type"]
comp_id			=d_obj["e"]				# again the compatition ID
comp_dayid		=d_obj["i"]				# the day ID
comp_date		=d_obj["d"]				# date in milliseconds from the Unix epoch 
comp_daytype		=d_obj["y"]				# day type: 1= valid, 2= practice, 3= canceled, 4= rest, 9= other
comp_daytitle		=d_obj["l"]				# day title
comp_shortdaytitle	=d_obj["t"]				# short day title
comp_starttime		=d_obj["a"]				# start time millis from midnite
comp_startaltitude	=d_obj["h"]				# start altitude
comp_finishaltitude	=d_obj["f"]				# finish altitude
print "Comp day:", comp_day, "Comp ID:", comp_id, "Comp ID DAY:", comp_dayid, "Title:", comp_daytitle, comp_shortdaytitle, "\nStart time (millis):", comp_starttime, "Start alt.:", comp_startaltitude, "Finish Alt.:", comp_finishaltitude
if "k" in d_obj:
	comp_taskinfo		=d_obj["k"]			# task infor data
else:
	print "No task for that day..."
	print "WARNING: No valid JSON file generated ....................."
	exit()
# event

#
# close the files and exit
#
if execopt:
    cwd=os.getcwd()
    print "Extracting the IGC file from embeded FLARM messages \nFrom CD:", cwd, "To:", dirpath+"/DAY"+str(day)
    os.chdir(dirpath+"/DAY"+str(day))                           # report current directory and the new one

    fname=FlarmID+'.'+getognreg(FlarmID)+'.'+getogncn(FlarmID)+'.igc'
    if os.path.isfile(fname):                                   # remove to avoid errors
        os.remove(fname)                                        # remove if exists
                                                                # get the new IGC files based on the FLARM messages
    os.system('grep "FLARM "'+FlarmID+' * | sort -k 3 | python '+cwd+'/genIGC.py '+FlarmID+' > '+fname)
    print "Resulting IGC file is on:", dirpath+"/DAY"+str(day), "As: ", fname

if npil == 0:
        exit(-1)
else:
        print "Pilots found ... ", npil
        print "=====================================================================: \n\n\n" 		# just a trace
        exit(0)


