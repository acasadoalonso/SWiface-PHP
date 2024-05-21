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
from ognddbfuncs import *
from geofuncs import convertline
from gistfuncs import *
#-------------------------------------------------------------------------------------------------------------------#
import config
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


#-------------------------------------------------------------------------------------------------------------------#
#
# arguments:   compid, dayindex, print
#		where compid is the assigned competition ID or 0 for the list of competitions.
#		dayindex is 0 for the first day, 1 second day, etc, ...
#		print is a falg to print the JSON input on pretty print
#


qsgpIDreq = sys.argv[1:]				# first arg is the event ID
dayreq = sys.argv[2:]					# second arg is the day index within the event
prtreq = sys.argv[3:]					# print request

                                                        # directory where to stor the JSON file generated
cucpath = config.cucFileLocation
tp = []							# turn pint list
tracks = []						# track list
version='V2.02'
if 'USER' in os.environ:
        user=os.environ['USER']
else:
        user="www-data"                     	# assume www

#

if qsgpIDreq and qsgpIDreq[0] != '0':
    qsgpID = sys.argv[1]
    if not qsgpID.isnumeric():

       print ("Please indicate the COMP ID\n\n")
       print ("Usage python sgp2sws.py COMPID indexday or http://host/SWS/sgp2sws.html")
       exit(-1)
    try:
       days = str(sys.argv[2])
    except:
       print ("Please indicate the index day\n\n")
       print ("Usage python sgp2sws.py COMPID indexday or http://host/SWS/sgp2sws.html")
       exit(-1)
    if days[0].isdigit():
        day = int(days)
        days = ''
    else:
        day = 0
else:
    qsgpID = '0'

if prtreq and prtreq[0] == "print":
    prt = True
else:
    prt = False

print("\n\nGenerate .json files from the www.sgp.aero web server. Version: "+version)
print("Usage python sgp2sws.py COMPID indexday or http://host/SWS/sgp2sws.html")
print("=======================================================================\n\n")
hostname = socket.gethostname()
print("DBhost:", config.DBhost, "ServerName:", hostname)
start_time = time.time()
local_time = datetime.datetime.now()
j = urllib.request.urlopen('https://www.crosscountry.aero/c/sgp/rest/comps/')
rr=j.read().decode('UTF-8') 
j_obj = json.loads(rr)
if qsgpID == '0':
    #print j_obj
    j = json.dumps(j_obj, indent=4)
    print(j)
    exit(0)
else:
    for xx in j_obj:
        if xx['id'] == int(qsgpID):
            print("Title:", xx['fullEditionTitle'])
    # print the time for information only
    print("CompID:", qsgpID, "Time is now:", local_time)

fl_date_time = local_time.strftime("%Y%m%d")            # get the local time
ts_date_time = local_time.strftime("%Y-%m-%d")          # get the local time
JSONFILE = cucpath + config.Initials + fl_date_time + \
    '.json'                                             # name of the JSON to be generated
TASKFILE = cucpath + config.Initials + fl_date_time + \
    '.tsk'                                              # name of the TASK to be generated
                                                        # name of the COMP to be generated
COMPFILE = cucpath + 'competitiongliders.lst'
                                                        # name of the COMP to be generated
CSVSFILE = cucpath + 'competitiongliders.csv'
print("JSON generated data file is: ", JSONFILE) 	# just a trace
print("TASK generated data file is: ", TASKFILE) 	# just a trace
print("COMP generated data file is: ", COMPFILE) 	# just a trace
print("CSVS generated data file is: ", CSVSFILE) 	# just a trace
print("===========================: ") 			# just a trace

if  os.path.isfile(JSONFILE):
  os.system('rm  '+JSONFILE)		                # remove the previous one
if  os.path.isfile(TASKFILE):
  os.system('rm  '+TASKFILE)		                # remove the previous one
if  os.path.isfile(COMPFILE):
  os.system('rm  '+COMPFILE)		                # remove the previous one
if  os.path.isfile(CSVSFILE):
  os.system('rm  '+CSVSFILE)		                # remove the previous one
                                                        # open the output file
jsonfile = open(JSONFILE, 'w')
                                                        # open the output file
taskfile = open(TASKFILE, 'w')
                                                        # open the output file
compfile = open(COMPFILE, 'w')
                                                        # open the output file
csvsfile = open(CSVSFILE, 'w')
#
# get the JSON string for the web server
#
j = urllib.request.urlopen('https://www.crosscountry.aero/c/sgp/rest/comp/'+str(qsgpID))
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
wlist = []
clist = []
flist = []                                		# Filter list for glidertracker.org
flist.append("ID,CALL,CN,TYPE,INDEX")   		# Initialize with header row
nwarnings = 0                                  		# number of warnings ...
warnings = []                                  		# warnings glider

#ogndata=getddbdata()                                    # get the OGN DDB
npil = 0				        	# number of pilots found
pilots = j_obj["p"]					# get the pilot information
print("Pilots:", len(pilots))
print("==========")
for id in pilots:
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
    if int(qsgpID) >= 14:
        flarmid = pilots[id]["q"].rstrip()              # flarm id
        registration = pilots[id]["w"].lstrip()         # registration
        if registration == "":
            print("Warning .... Missing glider registration:", flarmid, "\n\n")
            nwarnings += 1
            warnings.append(lname) 			# add it to the list of warnings
                                                        # get the FlarmId from the registration
        ognflarm = getognflarmid(registration)
        if len(flarmid) == 6:
            flarmid="FLR"+flarmid
        if flarmid == '':
                                                        # get the FlarmId from the registration
            flarmid = getognflarmid(registration)
        if ognflarm == '' or ognflarm == "NOFlarm":
            ognflarm = "***NOREG***"
            print("Warning .... Flarm not registered on the OGN DDB", flarmid, ognflarm, "\n\n")
            nwarnings += 1
            warnings.append(lname) 			# add it to the list of warnings

        elif flarmid[3:9] != ognflarm[3:9]:
            print("Warning .... Flarm on system is not the same that Flarms registered on OGN, on the SGP system:", flarmid, "and on the OGN DDB:", ognflarm, "\n\n")
            nwarnings += 1
            warnings.append(lname) 			# add it to the list of warnings
        if 't' in pilots[id] :				# if we have tracker paired ???
            ogntracker=pilots[id]['t'].upper().rstrip()	# OGN tracker to pair
        else:
            ogntracker=''
    else:
        flarmid = "FLRDDDDDD"				# older versions 
        registration = "EC-XXX"

    if flarmid != '':
        wlist.append(flarmid[3:9])			# add device to the white list
        clist.append(flarmid)				# add device to the competion list
        if ogntracker != '':
           clist.append(ogntracker)			# add pairing tracker to the competion list
        else:
           clist.append("OGNFFFFFF")			# add pairing tracker to the competion list
        flist.append(flarmid+","+registration+","+compid+"," +
                     model+","+str(1))                  # Populate the filter list
    else:
        warnings.append(lname) 				# add it to the list of warnings
        nwarnings += 1  				# and increase the number of warnings

    if hostname == "SWserver":				# deal with the different implementation of pycountry
                                                        # the the 3 letter country code
        ccc = pycountry.countries.get(alpha_2=country)
        country = ccc.alpha_3				# convert to a 3 letter code
    else:
                                                        # the the 3 letter country code
        ccc = pycountry.countries.get(alpha_2=country)
        country = ccc.alpha_3				# convert to a 3 letter code
    if country in Flags:                                # if it a known country ???
        color = Flags[country]                          # use the predefined colots
    else:                                               # use ramdom colors
        rgb=0x111*int(id)                               # the the RGB color
        ccc=hex(rgb)                                    # convert it to hex
        color="#"+ccc[2:]                               # set the JSON color required

    pilotname = str((fname+" "+lname).encode('utf8').decode('utf-8'))
    if flarmid == ognflarm and registration != "":
       flarmOK = "OK"
    else:
       flarmOK = "NOTOK"
    print("Pilot:", pid, pilotname, compid, country, model, j, rankingid, registration, "SGP FlarmID:", flarmid, "OGN:", ognflarm, flarmOK  ,"Tracker:", ogntracker)
    print("FlarmID on SYS:", flarmid, "Flarm reg:", ognflarm, "Registration:", registration)
    if config.PicPilots == 'FAI':                       # use the FAI ranking List for the pilot photos ???
        p = urllib.request.urlopen('https://rankingdata.fai.org/rest01/api/rlpilot?id='+str(rankingid))
        rr=p.read().decode('UTF-8') 
        pr = json.loads(rr)
        photourl="http://rankingdata.fai.org/PilotImages/noimage.jpg"
        #print("PR", pr)
        if pr != None:                                  # use the RankingList API
            obj=pr['data']   		                # reach the photo file
            if obj != None:
               on=obj[0]
               photo=on['photo']				# get the photo file
               photourl="http://rankingdata.fai.org/PilotImages/"+photo
               print    ("wget "+photourl+" -q -O PilotImages/"+photo)
               os.system("wget "+photourl+" -q -O PilotImages/"+photo)
               photourl=config.SWSserver+"SWS/PilotImages/"+photo
           
            if photo == "noimage.jpg":
               #print("PPP", config.SWSserver+"SWS/PilotImages/"+str(rankingid)+".jpg")
               if os.path.exists("PilotImages/"+str(rankingid)+".jpg"):
                  photourl=config.SWSserver+"SWS/PilotImages/"+str(rankingid)+".jpg"
               else:
                  print("Photo not found")
               
        #print ("PhotoURL: ", pilotname, "RankingID:", rankingid, "==>>",photourl)
        tr = {"trackId": config.Initials+fl_date_time+":"+flarmid, "pilotName": pilotname,  "competitionId": compid, "country": country, "aircraft": model,
              "registration": registration, "3dModel": "ventus2", "ribbonColors": color, "portraitUrl": photourl, "ognTrackerPaired": ogntracker}
    else:                                               # use the local pictures on the SWS server
        tr = {"trackId": config.Initials+fl_date_time+":"+flarmid, "pilotName": pilotname,  "competitionId": compid, "country": country, "aircraft": model, "registration": registration,
              "3dModel": "ventus2", "ribbonColors": color, "portraitUrl": config.SWSserver+"SWS/pic/"+compid+".png", "3dModelVariant": config.SWSserver+"SWS/pic/"+compid+".sponsor.png"}
                                                        # add it to the tracks
    tracks.append(tr)
    npil += 1						# increase the number of pilots
    print("---------------------")

#print tracks
print("Wlist:", wlist)
print("===========")
print("Competition")
print("===========")
comp = j_obj["c"]					# get the competition information
comp_firstday = comp['a']				# first day of the competition
comp_lastday = comp['b']				# last day of the competition
comp_name = comp['t']				        # event name
comp_shortname = comp['l']				# event short name
comp_id = comp['i']
print("Comp ID:", comp_id, "Name:", comp_name, "Short name:", comp_shortname, "First day:",comp_firstday, "Last day:", comp_lastday, "Number of pilots:", npil)
numberofactivedays = 0

if j_obj.get("j") != None:
    numberofactivedays = j_obj["j"]
if j_obj.get("i") == None:				# check if is fully setup the web site
    print("No index of days ... exiting.")
    print("WARNING: No valid JSON file generated .....................")
    os.system('rm  '+JSONFILE)		                # remove the previous one
    os.system('rm  '+TASKFILE)		                # remove the previous one
    os.system('rm  '+COMPFILE)		                # remove the previous one
    os.system('rm  '+CSVSFILE)		                # remove the previous one
    exit(-1)
indexofdays = j_obj["i"]
                                                        #print "Index of Days", indexofdays
if days != '':
    cday = 0
    for dayday in indexofdays:
        #print "DAYDAY", days, dayday
        if dayday["l"].upper() == days.upper():
            day = cday
            break
        else:
            cday += 1
            continue

date = indexofdays[day]["d"]			        # date
title = indexofdays[day]["t"] 			        # day tittle
shorttitle = indexofdays[day]["l"]    		        # day short title
starttime = indexofdays[day]["a"]    		        # start time millis from midnite
daytype = indexofdays[day]["y"]    		        # day type: 1, 2, 3 ...
dayid = indexofdays[day]["i"] 			        # day ID
print("DATE:", date, "Title:", title, "Day:", shorttitle, "==>", day, "\nStart time(millis):", starttime, "Day type:", daytype, "Day ID:", dayid, "Number of active days:", numberofactivedays)
if date != ts_date_time:
    print ("Warning the task date is not TODAY !!!")
    nwarnings += 1
    warnings.append("<<DATE>>") 			        # add it to the list of warnings

d = urllib.request.urlopen(
    'https://www.crosscountry.aero/c/sgp/rest/day/'+str(qsgpID)+'/'+str(dayid))
rr=d.read().decode('UTF-8') 
d_obj = json.loads(rr)
if prt:
    print("____________________________________________________________")
    d = json.dumps(d_obj, indent=4)
    print(d)
if numberofactivedays == 0:
    print("No active days ...")

print("=============================")
print("Day: ", day, "DayID: ", dayid)
print("=============================")
#print( "DDD", d_obj)
comp_day = d_obj["@type"]
comp_id = d_obj["e"]				        # again the compatition ID
comp_dayid = d_obj["i"]				        # the day ID
comp_date = d_obj["d"]				        # date in milliseconds from the Unix epoch
# day type: 1= valid, 2= practice, 3= canceled, 4= rest, 9= other
comp_daytype = d_obj["y"]
if 'l' in d_obj:					#check if  day title
   comp_daytitle = d_obj["l"]				# day title
else:
   comp_daytitle =  'NoDay'				# day title
if 't' in d_obj:					#check if  day title
   comp_shortdaytitle = d_obj["t"]				# short day title
else:
   comp_shortdaytitle = 'Noday'
comp_starttime = d_obj["a"]				# start time millis from midnite
comp_startaltitude = d_obj["h"]				# start altitude
comp_finishaltitude = d_obj["f"]			# finish altitude
print("Comp day:", comp_day, "Comp ID:", comp_id, "Comp ID DAY:", comp_dayid, "Title:", comp_daytitle, comp_shortdaytitle, "\nStart time (millis):", comp_starttime, "Start alt.:", comp_startaltitude, "Finish Alt.:", comp_finishaltitude)
if "k" in d_obj:
    comp_taskinfo = d_obj["k"]			        # task infor data
else:
    print("No task for that day...")
    print("WARNING: No valid JSON file generated .....................")
                                                        # remove the previous one
    os.system('rm  '+JSONFILE)
                                                        # remove the previous one
    os.system('rm  '+TASKFILE)
    os.system('rm  '+COMPFILE)		                # remove the previous one
    os.system('rm  '+CSVSFILE)		                # remove the previous one
    exit()
task_type = comp_taskinfo["@type"]
task_id = comp_taskinfo["id"]
task_listid = comp_taskinfo["taskListId"]
task_name = comp_taskinfo["name"]
task_data = comp_taskinfo["data"]
task_creator = comp_taskinfo["creator"]		        # creator
task_description = comp_taskinfo["description"]		# description of the task
task_desc = json.loads(task_description)
task_length = task_desc["d"]				# task length
task_atfrom = task_desc["ta"]			        # task from

task_at = task_data["at"]
task_wp = task_data["g"]
task_wpla = task_data["u"]
task_wptlist = task_wpla["wptList"]
task_at_country = task_at["c"]
task_at_timezone = task_at["z"]
task_at_elevation = task_at["e"]
task_at_place = task_at["n"]
task_at_altitude = task_at["e"]
task_at_runwaydir = task_at["d"]
task_at_runwaywidth = task_at["w"]
task_at_runwaysurface = task_at["f"]
task_at_runway = task_at["f"]
task_at_runways = task_at["k"]
if task_at.get("j") != None:
    task_at_icao = task_at["j"]
else:
    task_at_icao = "NOID"

task_at_source = task_at["s"]

if task_at.get("q") != None:
    task_at_freq = task_at["q"]
else:
    task_at_freq = 0

print("Task info")
print("=========")
print("Tasks type:", task_type, "ID:", task_id, task_listid, "Task Name:", task_name, "Airfield:", task_at_place, "TimeZone:", task_at_timezone)
#print "Task at:", task_at, "WPLA", task_wpla
print("Task country:", task_at_country, "at", task_at_place, "TZ:", task_at_timezone, "Elevation:", task_at_elevation, "Task Runway:", task_at_runway, task_at_runways, task_at_runwaydir, task_at_runwaywidth, task_at_runwaysurface, "Freq:", task_at_freq, "ICAO code:", task_at_icao)
print("Task creator:", task_creator, "\nTask length:", task_length, "From:", task_atfrom)
print("Number of WP#:", len(task_wp))
print("Waypoints of the task")
print("=====================")
#
wp = 0
legs = []
tptype=[]
while wp < len(task_wp):
    #print ("WP: ", task_wp[wp])
    wp_name = task_wp[wp]["n"]                          # waypoint name
    wp_name = "TP"+str(wp)+"-"+wp_name
    if wp == 0:
        wpinit = wp_name
        type = "Start"
        wp_name = "START"
    else:
        type = "Turnpoint"
    wp_lat = task_wp[wp]["a"]                           # latitude
    wp_lon = task_wp[wp]["o"]                           # longitude
    wp_type = task_wp[wp]["y"]                          # type: line or cylinder
    if "r" in task_wp[wp]:
       wp_radius = task_wp[wp]["r"]                     # cylinder radius or line length
    else:
       wp_radius = 500
    if wp > 0 and (wp_name == wpinit or wp_type == "line"):
        isbreak = True
        type = "Finish"
    if wp_type == "cylinder":
        oz = "Cylinder"
    else:
        oz = "Line"
    # wp_id			=task_wp[wp]["id"]	# Wyapoint ID
    if type == "Start":
        tptexture = config.SWSserver+"SWS/tptextures/START.png"
    elif type == "Finish":
        tptexture = config.SWSserver+"SWS/tptextures/FINISH.png"
        wp_name = "FINISH"
    else:
        tptexture = config.SWSserver+"SWS/tptextures/TP"+str(wp)+".png"
    print("WP:", wp_name, wp_lat, wp_lon,  wp_type, wp_radius, type, oz, tptexture)
    if type == 'Start' :
       tpx = {"latitude": wp_lat, "longitude": wp_lon, "name": wp_name, "observationZone": oz,
           "type": type, "radius": wp_radius, "trigger": "Enter", "texture": tptexture, "StartAltitude": comp_startaltitude}
    elif type == 'Finish':
       tpx = {"latitude": wp_lat, "longitude": wp_lon, "name": wp_name, "observationZone": oz,
           "type": type, "radius": wp_radius, "trigger": "Enter", "texture": tptexture, "FinishAltitude": comp_finishaltitude}
    else:
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

print("WP:================================>")
# event

print("Comp short name:", comp_shortname)
print("Comp full  name:", comp_name)
print("Comp date:", comp_date)
print("Comp Start time:", comp_starttime/1000)
#print tp
task = {"taskType": "SailplaneGrandPrix", "taskName": "SGPrace", "Airfield": task_at_place, "Elevation": task_at_elevation, "Runway": task_at_runway+" "+task_at_runways, "ICAOcode":task_at_icao, "TimeZone": task_at_timezone, 
        "compDate": comp_date, "startOpenTs": comp_starttime/1000, "turnpoints": tp} 
event = {"name": comp_shortname, "description": comp_name,
         "task": task, "tracks": tracks}
j = json.dumps(event, indent=4)
jsonfile.write(j)
print("Task end:==========================>")
print("Generate TSK file ...")
tsk = {"name": "SGPrace", "color": "0000FF", "legs": legs, "TPpointstype": tptype, "wlist": wlist}
tsks = []
tsks.append(tsk)
tasks = {"tasks": tsks}
tasks = convertline(tasks)                              # convert the start line on 3 point that will draw an START line
t = json.dumps(tasks, indent=4)                         # dump it
#print j
                                                        # write it into the task file on json format
taskfile.write(t)
j = json.dumps(clist, indent=4)                         # dump it
#print j
                                                        # write it into the comp file on json format
compfile.write(j)
compfile.close()


#
# close the files and exit
#

jsonfile.close()
taskfile.close()
latest = cucpath+config.Initials+'/SGPrace-latest.tsk'
latestj = cucpath+config.Initials+'/SGPrace-latest.json'
print("Linking:", TASKFILE+' ==>  '+latest)             # print is as a reference
if os.path.islink(latest):
   os.system('rm  '+latest)                             # remove the previous one
   os.system('rm  '+latestj)                            # remove the previous one
try:
    os.system('ln -s '+TASKFILE+' '+latest) 		# link the recently generated file now to be the latest !!!
    os.system('ln -s '+JSONFILE+' '+latestj) 		# link the recently generated file now to be the latest !!!
except:
    print("No latest file ...: ", latest)
if config.GIST:
   content=t+"\n"
   GIST_TOKEN= unobscure(config.GIST_TOKEN.encode()).decode()
   res=updategist(config.GIST_USER, "SGP RACING latest task", GIST_TOKEN, TASKFILE, content)
   print ("GIST RC: ", res.status_code)
   if res.status_code == 200 or res.status_code == 201:
      id=res.json()['id']
      print("https://gist.githubusercontent.com/"+config.GIST_USER+"/"+id+"/raw/")
   else:
      print("Error on GIST ....", res.status_code)

# Write a csv file of all gliders to be used as filter file for glidertracker.org
for item in flist:
    csvsfile.write("%s\n" % item)
csvsfile.close()
# change the chmod 
os.chmod(TASKFILE, 0o777)                               # make the TASK file accessible
os.chmod(JSONFILE, 0o777)                               # make the JSON file accessible
os.chmod(COMPFILE, 0o777)                               # make the COMP file accessible
os.chmod(CSVSFILE, 0o777)                               # make the CSVS file accessible
if user == "root":					# change the chown
       os.system ("chown www-data:www-data "+COMPFILE) 	# in case of root
       os.system ("chown www-data:www-data "+TASKFILE) 	# in case of root
       os.system ("chown www-data:www-data "+JSONFILE) 	# in case of root
       os.system ("chown www-data:www-data "+CSVSFILE) 	# in case of root
                                                        # the latest TASK file to be used on live.glidernet.org
if npil == 0:
    print("JSON invalid: No pilots found ... ")
    os.system('rm  '+JSONFILE)		                # remove the previous one
    os.system('rm  '+TASKFILE)		                # remove the previous one
    os.system('rm  '+COMPFILE)		                # remove the previous one
    os.system('rm  '+CSVSFILE)		                # remove the previous one
    exit(-1)
else:
    print("Pilots found ... ", npil, "Warnings:", nwarnings)
    if nwarnings > 0:
        print("Pilots with no FLARMID: ", warnings)
    exit(0)
