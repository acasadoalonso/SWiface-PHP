#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#
#   This script get the dat from the Strelpa.de server and gen the SW JSON file
#
import sys
import json
import urllib.request, urllib.error, urllib.parse
import time
from dateutil.parser import parse
from datetime import timedelta
import datetime

import os
import math
import pycountry
import socket
from ognddbfuncs import *
from geofuncs import convertline
import config
from dummyfile import fixcoding
#-------------------------------------------------------------------------------------------------------------------#
global wlist 
global clist 
global flist 
global nwarnings 
global warnings 
wlist = []
clist = []
flist = []                                		# Filter list for glidertracker.org
flist.append("ID,CALL,CN,TYPE,INDEX")   		# Initialize with header row
nwarnings = 0                                  		# number of warnings ...
warnings = []                                  		# warnings glider
#-------------------------------------------------------------------------------------------------------------------#
Flags = { 						# flag colors assigned to the countries
    "ESP": ["red", "yellow", "red"],
    "AUS": ["yellow", "green", "yellow"],
    "AUT": ["red", "white", "red"],
    "CHL": ["white", "blue", "white"],
    "SVN": ["white", "red", "blue"],
    "FRA": ["blue", "white", "red"],
    "NLD": ["red", "white", "blue"],
    "CHE": ["red", "red", "red"],
    "LTU": ["yellow", "green", "red"],
    "ITA": ["green", "white", "red"],
    "GBR": ["red", "white", "blue"],
    "BEL": ["black", "yellow", "red"],
    "DEU": ["black", "red", "yellow"],
    "NZL": ["blue", "blue", "blue"],
    "CZE": ["white", "blue", "red"],
    "POL": ["white", "red", "white"],
    "RUS": ["white", "blue", "red"],
    "SWE": ["blue", "yellow", "white"],
    "NOR": ["blue", "red", "red"],
    "ZAF": ["red", "green", "yellow"],
    "HKG": ["red", "white", "red"],
    "USA": ["red", "blue", "red"]
}


#-------------------------------------------------------------------------------------------------------------------#
def getpilots(pilots, tclass, prt=False):
  global wlist 
  global clist 
  global flist 
  global nwarnings 
  global warnings 
  npil=0
  tracks = []						# track list
  wlist  = []						# init the wlist for this class
  clist  = []						# init the wlist for this class
  flist  = []						# init the wlist for this class
  flist.append("ID,CALL,CN,TYPE,INDEX")   		# Initialize with header row
  for entry  in pilots:
    #
    pid   	= entry["id"]                           # get the pilot ID
    name 	= entry["name"]                         # first name
    name        = name.encode('utf8').decode('utf8')
    name        = fixcoding(name)
    compid 	= entry["glider_cid"]                   # competition number
    country 	= entry["country"][0:3]                 # three letters country code
    model 	= entry["glider_name"]                  # aircraft model
    registration = entry["glider_callsign"]            	# registration
    flarmid 	= entry["flarm_ID"][2:]                	# flarm id
    flarmtype   = entry["flarm_ID"][0:2]		# just the flarm type ICA|FLR|OGN
    classname 	= entry["className"]                    # Class
    if classname != tclass:
       continue
    if prt:
       print("---------------------")
    rankingid 	= 0
    if registration == "":
            if prt:
               print(">>>: Warning .... Missing glider registration:", flarmid, "\n\n")
            nwarnings += 1
            warnings.append(name) 			# add it to the list of warnings
                                                        # get the FlarmId from the registration
    ognflarm = getognflarmid(registration)
    if prt:
       print("FlarmID on SYS:", entry["flarm_ID"], "OGN Flarm reg:", ognflarm, "Registration:", registration)
    if len(flarmid) == 6:
            if  flarmtype == '05':
                flarmid="ICA"+flarmid
            elif flarmtype == '07':
                flarmid="OGN"+flarmid
            else:
                flarmid="FLR"+flarmid
    if flarmid == '':
                                                        # get the FlarmId from the registration
            flarmid = getognflarmid(registration)
    if ognflarm == '' or ognflarm == "NOFlarm":
            flarm = "***NOREG***"
            if prt:
               print(">>>: Warning .... Flarm not registered on the OGN", flarmid, ognflarm, "\n")
            nwarnings += 1
            warnings.append(name) 			# add it to the list of warnings

    elif flarmid[3:9] != ognflarm[3:9]:
            if prt:
               print(">>>: Warning .... Flarm on system is not the same that Flarms registered on OGN, system:", flarmid, "OGN:", ognflarm, "\n")
            nwarnings += 1
            warnings.append(name) 			# add it to the list of warnings
    if flarmid != '':
        wlist.append(flarmid[3:9])			# add device to the white list
        clist.append(flarmid)				# add device to the white list
        flist.append(flarmid+","+registration+","+compid+"," +
                     model+","+str(1))                  # Populate the filter list
    else:
        warnings.append(name) 				# add it to the list of warnings
        nwarnings += 1  				# and increase the number of warnings

    if country in Flags:                                # if it a known country ???
        color = Flags[country]                          # use the predefined colots
    else:                                               # use ramdom colors
        rgb=0x111*int(pid)                              # the the RGB color
        ccc=hex(rgb)                                    # convert it to hex
        color="#"+ccc[2:]                               # set the JSON color required

    pilotname = name.encode('utf8').decode('utf-8')
    if prt:
       print("Pilot:", pid, name, compid, country, model, rankingid, registration, "FlarmID:", flarmid, "OGN:", ognflarm)
    if config.PicPilots == 'FAI':                       # use the FAI ranking List for the pilot photos ???
        p = urllib.request.urlopen('https://rankingdata.fai.org/rest01/api/rlpilot?id='+str(rankingid))
        rr=p.read().decode('UTF-8') 
        pr = json.loads(rr)
        if pr != None:                                  # use the RankingList API
            obj=pr['object_name']                       # reach the photo file
            on=obj[0]
            photo=on['photo']
            photourl="http://rankingdata.fai.org/PilotImages/"+photo
        else:
            photourl="http://rankingdata.fai.org/PilotImages/noimage.jpg"
        if prt:
           print ("PhotoURL: ", pilotname, "RankingID:", rankingid, "==>>", url)
        tr = {"trackId": config.Initials+fl_date_time+":"+flarmid, "pilotName": pilotname,  "competitionId": compid, "country": country, "aircraft": model,
              "registration": registration, "3dModel": "ventus2", "ribbonColors": color, "portraitUrl": photourl}
    else:                                               # use the local pictures on the SWS server
        tr = {"trackId": config.Initials+fl_date_time+":"+flarmid, "pilotName": pilotname,  "competitionId": compid, "country": country, "aircraft": model, "registration": registration,
              "3dModel": "ventus2", "ribbonColors": color, "portraitUrl": config.SWSserver+"SWS/pic/"+compid+".png", "3dModelVariant": config.SWSserver+"SWS/pic/"+compid+".sponsor.png"}
                                                        # add it to the tracks
    tracks.append(tr)
    npil += 1						# increase the number of pilots
    if prt:
       print("---------------------")
  return (tracks)

#-------------------------------------------------------------------------------------------------------------------#
							# get the task information
def gettask(ct, cdID, ccID, fptask, prt=False):		# competition ID, competition day ID. competition class ID

   global wlist
   tptype=[]
   wp = 0
   legs = []
   if prt:
        j = json.dumps(j_obj, indent=4)
        print (j)
   activeTask=ct['activeTask']
   tasks     =ct['tasks']
   for tt in tasks:
       tid=tt['id']
       name=tt['name'].encode('utf8').decode('utf8')
       if int(tid) != int(activeTask):
          print (">>>>>>Not the main task: >%s<>%s<"% (tid, activeTask), name)
          continue
       distance=tt['distance']
       numLegs=tt['numLegs']
       rule=tt['rule']
       task_wp=tt['tps']
       #print ("TTT:", tid, name, distance, task_wp)
       while wp < len(task_wp):
           wp_name = task_wp[wp]['tp']["name"].encode('utf8').decode('utf8')          # waypoint name
           wp_name = "TP"+str(wp)+"-"+wp_name
           if wp == 0:
               wpinit = wp_name
               type = "Start"
               wp_name = "START"
           else:
               type = "Turnpoint"
           wp_lat      = task_wp[wp]['tp']["lat"]       # latitude
           wp_lon      = task_wp[wp]['tp']["lng"]       # longitude
           wp_type     = task_wp[wp]['scoring']["type"] # type: line or cylinder
           if wp_type == "KEYHOLE":
              wp_radius   = task_wp[wp]['scoring']["radiusCylinder"]  # cylinder radius or line length
              wp_radiusSector = task_wp[wp]['scoring']["radiusSector"]  # cylinder radius or line length
              wp_angle        = task_wp[wp]['scoring']["angle"]         # angle to FAI thistle
           elif wp_type == "LINE":
              wp_radius   = task_wp[wp]['scoring']["width"]  # cylinder radius or line length
           else:
              wp_radius   = 0
           if wp > 0 and (wp_name == wpinit or wp_type == "LINE"):
               isbreak = True
               type = "Finish"
           if wp_type == "KEYHOLE":
               oz = "Cylinder"
           else:
               oz = "Line"

           if type == "LINE" and wp==0 :
               tptexture = config.SWSserver+"SWS/tptextures/START.png"
           elif wp == len(task_wp) -1 :
               tptexture = config.SWSserver+"SWS/tptextures/FINISH.png"
               wp_name = "FINISH"
           else:
               tptexture = config.SWSserver+"SWS/tptextures/TP"+str(wp)+".png"
           print("WP>>:", wp_name, wp_lat, wp_lon,  wp_type, wp_radius, type, oz, tptexture)
           tpx = {"latitude": wp_lat, "longitude": wp_lon, "name": wp_name, "observationZone": oz,
                  "type": type, "radius": wp_radius, "trigger": "Enter", "texture": tptexture}
           tp.append(tpx)
           tlegs = [wp_lat, wp_lon]
           legs.append(tlegs)
           trad = [wp_radius]
           legs.append(trad)
           tptype.append(oz)                       # save the turning point ype

           if wp > 0 and (wp_name == wpinit or wp_type == "line"):
               break
           wp += 1

   print("Task info for class:", cname, "Task name:", name)
   print("===============================================")
   print("Tasks type:", rule, "ID:", tid,  "Task Name:", name, "Distance:", distance, "Number of legs:", numLegs)
   print("Number of WP#:", len(task_wp), "\n")
#
       
   local_time = datetime.utcnow()      			# the local time
                                                	# build the event
                                                	# event
   y = local_time.year
   m = local_time.month
   d = local_time.day
                                                 	# number of second until beginning of the day
   td = datetime(y, m, d)-datetime(1970, 1, 1)
                                                	# timestamp 09:00:00 UTC
   ts = int(td.total_seconds()+9*60*60)
   tsk = {"name": name , "color": "0000FF", "legs": legs, "TPpointstype": tptype, "wlist": wlist}
   tsks = []
   tsks.append(tsk)
   print("Generate TSK file ...")
   tasks = {"tasks": tsks}
   tasks = convertline(tasks)                  		# convert the START line on 3 point that will draw a line
                                                	# files that contains the latest TASK file to be used on live.glidernet.org
   j = json.dumps(tasks, indent=4)             		# dump it
   #print j
                                                	# write it into the task file on json format
   taskfile.write(j)
   taskfile.close()                            		# close the TASK file for this class
   swstask={ "taskName": name, "taskType": rule, "startOpenTs": ts, "turnpoints": tp}
   return(swstask)
#-------------------------------------------------------------------------------------------------------------------#
#
# arguments:   compid, dayindex, print
#		where compid is the assigned competition ID or 0 for the list of competitions.
#		dayindex is 0 for the first day, 1 second day, etc, ...
#		print is a falg to print the JSON input on pretty print
#


qcomIDreq = sys.argv[1:]			# first arg is the event ID
dayreq = sys.argv[2:]				# second arg is the day index within the event
prtreq = sys.argv[3:]				# print request

                                                # directory where to stor the JSON file generated
cucpath = config.cucFileLocation
initials = config.Initials		        # initials of the files generated

tp = []						# turn pint list
tracks = []					# track list
version='V1.00'
#

if qcomIDreq and qcomIDreq[0] != '0':
    qcomID = sys.argv[1]
    qdays = str(sys.argv[2])
    if qdays[0].isdigit():
        day = int(qdays)
        qdays = ''
    else:
        day = 0
else:
    qcomID = '0'

if prtreq and prtreq[0] == "print":
    prt = True
else:
    prt = False

print("\n\nGenerate .json files from the strepla.de web server. Version: "+version)
print("Usage python str2sws.py COMPID indexday or http://host/SWS/sgp2sws.html")
print("=======================================================================\n\n")
hostname = socket.gethostname()
print("DBhost:", config.DBhost, "ServerName:", hostname, "\n\n")
start_time = time.time()
local_time = datetime.datetime.now()
URLbase='http://www.strepla.de/scs/ws/'
j = urllib.request.urlopen(URLbase+'competition.ashx?cmd=active&daysPeriod=360')
rr=j.read().decode('UTF-8') 
j_obj = json.loads(rr)
#print(j_obj)
if qcomID == '0':
    #print j_obj
    j = json.dumps(j_obj, indent=4)
    print(j)
    exit(0)
else:
    
    for xx in j_obj:
        if xx['id'] == int(qcomID):
            print("Title:", xx['name'], "First day:", xx["firstDay"], "Last day", xx["lastDay"], "\n\n")
            compinfo=xx
    # print the time for information only
    print("CompID:", qcomID, "Time is now:", local_time)

fl_date_time = local_time.strftime("%Y%m%d")            # get the local time
ts_date_time = local_time.strftime("%Y-%m-%d")          # get the local time
#
# get the JSON string for the web server - Competitors
#
url=URLbase+'pilot.ashx?cmd=competitors&cId='+str(qcomID)
#print(url)
j = urllib.request.urlopen(url)
rr=j.read().decode('UTF-8') 
j_obj = json.loads(rr)
if prt:
    #print j_obj
    j = json.dumps(j_obj, indent=4)
    print(j)
    exit(0)
#
# the different pieces of information
#

pilots = j_obj						# get the pilot information
print("===========")
print("Competition")
print("===========")
comp_firstday 	= compinfo['firstDay']			# first day of the competition
comp_lastday 	= compinfo['lastDay']			# last day of the competition
comp_name 	= compinfo['name']		        # event name
comp_shortname 	= compinfo['description']		# event short name
comp_id 	= compinfo['id']
print("Comp short name:", comp_shortname)
print("Comp full  name:", comp_name)
print("Comp date:", comp_firstday)
from datetime import datetime
fday=parse(comp_firstday)
lday=parse(comp_lastday)
tdays=(lday-fday).days
print("Comp ID:", comp_id, "Name:", comp_name, "Short name:", comp_shortname, "\nFrom:",  comp_firstday, "Till:", comp_lastday, tdays, "days of competition\n\n")
numberofactivedays = tdays

ourday=fday+timedelta(seconds=day*24*60*60)		# our day
ourdate=ourday.isoformat()
npil = len(pilots)				       	# number of pilots found
print("Pilots:", len(pilots))
print("==========")
if tdays == 0:
    print("No index of days ... exiting.")
    print("WARNING: No valid JSON file generated .....................")
    exit(-1)
                                                        #print "Index of Days", indexofdays

if numberofactivedays == 0:
    print("No active days ...")
    exit(-1)

#
# get the JSON string for the web server (competition days)
#
url=URLbase+'results.ashx?cmd=overviewDays&cID='+str(qcomID)
#print(url)
j = urllib.request.urlopen(url)
rr=j.read().decode('UTF-8') 
j_obj = json.loads(rr)
j = json.dumps(j_obj, indent=4)
#print(j)
#
compdays=j_obj						# competition days
#
# get the JSON string for the web server (competition days)
#
url=URLbase+'compclass.ashx?cmd=overview&cID='+str(qcomID)
#print(url)
j = urllib.request.urlopen(url)
rr=j.read().decode('UTF-8') 
j_obj = json.loads(rr)
j = json.dumps(j_obj, indent=4)
#print(j)
#
cdate=''
filenames=False
lclases=j_obj						# list of clases
# --------------------------------------------------------------------------
for cl in lclases:
    cid=cl['id']
    cname=cl['name']					# classname
    rname=cl['rulename']				# racing|AAT
    for cd in compdays:
        if cname != cd['nameCC']:
           continue
        cdate = cd["date"] 			        # date
        state = cd["state"] 			        # status
        sState = fixcoding(cd["sState"])	        # status named
        idCD  = cd["idCD"] 			        # competition day
        idCC  = cd["idCC"] 			        # competition class
        if cdate != ourdate:				# is our date
           continue
        print("======================================================================")
        print("Day: ", day, "DayID: ", idCD, "Class:", cname, "Status:", state, sState)
        print("======================================================================")
        JSONFILE = cucpath + initials + fl_date_time+"-"+cname+".json"
        TASKFILE = cucpath + initials + fl_date_time+"-"+cname+".tsk"
        CSVFILE  = cucpath + initials + fl_date_time+"-"+cname+"filter.csv"
                                                # name of the JSON to be generated, one per class

        if os.path.isfile(JSONFILE):
         os.system('rm  '+JSONFILE)		        # delete the JSON & TASK files
        if os.path.isfile(TASKFILE):
         os.system('rm  '+TASKFILE)
        if os.path.isfile(CSVFILE):
         os.system('rm  '+CSVFILE)
        print("JSON generated data file for the class is: ", JSONFILE)  # just a trace
        print("TASK generated data file for the class is: ", TASKFILE)  # just a trace
        print("CSV  generated data file for the class is: ", CSVFILE)  # just a trace
        jsonfile = open(JSONFILE, 'w')		# open the output file, one per class
        taskfile = open(TASKFILE, 'w')		# open the output file, one per class
        csvfile = open(CSVFILE, 'w')		# open the output file, one per class
        filenames=True


#
# get the JSON string for the web server (task info)
#
        url=URLbase+'results.ashx?cmd=task&cID='+str(qcomID)+'&idDay='+str(idCD)+'&activeTaskOnly=true'
        #print(url)
        try:
           j = urllib.request.urlopen(url)
        except:
           continue
        rr=j.read().decode('UTF-8') 
        j_obj = json.loads(rr)

        tracks=getpilots(pilots, cname)			# get the pilots of that class
        tsk=gettask(j_obj, idCD, idCC, taskfile, prt=False)	# get the task info

        #print ("TSKTSK", tsk)
        j = json.dumps(tsk, indent=4)                   # dump it
        #print (j)
        if len(tsk) == 0:
           print("No task for that day...")
           print("WARNING: No valid JSON file generated .....................")
                                                        # remove the previous one
           os.system('rm  '+JSONFILE)
                                                        # remove the previous one
           os.system('rm  '+TASKFILE)
           os.system('rm  '+COMPFILE)		        # remove the previous one
           os.system('rm  '+CSVSFILE)		        # remove the previous one
           exit(-1)
        npilots=len(tracks)
        #print ("TRACKS:", tracks)
        print("Class:", cname, "DATE:", cdate, "NPilots:", npilots, "Status:", state, "C Day:", idCD, "==>", idCC, "\n")
        #print("Wlist:", wlist)
        event = {"name": comp_name+"-"+cname, "description": cname,  "eventRevision": 0, "task": tsk,  "tracks": tracks}

        j = json.dumps(event, indent=4)             	# dump it
                                                	# write it into the JSON file
        jsonfile.write(j)
        jsonfile.close()                            	# close the JSON file for this class
        os.chmod(JSONFILE, 0o777) 			# make the JSON file accessible
        #print j
                                                	# files that contains the latest TASK file to be used on live.glidernet.org

        os.chmod(TASKFILE, 0o777) 			# make the TASK file accessible
        latest = cucpath+initials+'/'+cname+'-latest.tsk'
        print(TASKFILE+' ==>  '+latest)			# print is as a reference
        try:
            os.system('rm  '+latest)			# remove the previous one
        except:
            print("No previous latest task file")
                                                	# link the recently generated file now to be the latest !!!
        try:
            os.link(TASKFILE, latest)
        except:
            print("error on link")



# end of loop of classes 


# ------------------------------------------------------------------
if cdate != ts_date_time:
    print ("\n>>>: Warning the task date is not TODAY !!!\n")
    nwarnings += 1
    warnings.append("<< DATE NOT TODAY !!! >>")	        # add it to the list of warnings


print("Task end:==========================>")
# ------------------------------------------------------------------
#
# close the files and exit
#
if filenames:

   jsonfile.close()
   taskfile.close()
   os.chmod(TASKFILE, 0o777)                               # make the TASK file accessible
   os.chmod(JSONFILE, 0o777)                               # make the JSON file accessible
   os.chmod(CSVFILE, 0o777)                                # make the CSV  file accessible
                                                        # the latest TASK file to be used on live.glidernet.org
# Write a csv file of all gliders to be used as filter file for glidertracker.org
#for item in flist:
    #csvsfile.write("%s\n" % item)
if npil == 0:
    print(">>>: ERROR: JSON invalid: No pilots found ... ")
    os.system('rm  '+JSONFILE)		                # remove the previous one
    os.system('rm  '+TASKFILE)		                # remove the previous one
    os.system('rm  '+COMPFILE)		                # remove the previous one
    os.system('rm  '+CSVFILE)		                # remove the previous one
    exit(-1)
else:
    print("Pilots found ... ", npil, "Warnings:", nwarnings)
    if nwarnings > 0:
        print(">>>: Warning: Pilots with no FLARMID: ", warnings)
    print("Now:", local_time, "\n=======================================================================================================================================\n")
    exit(0)
