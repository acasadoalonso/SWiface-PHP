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
import kglid
#-------------------------------------------------------------------------------------------------------------------#
import config
Flags = { 						# flag colors assigned to the countries
	"ESP" : ["red", "yellow", "red"],
	"AUT" : ["red", "white", "red"],
	"CHL" : ["white", "blue", "white"],
	"SVN" : ["white", "red", "blue"],
	"FRA" : ["blue", "white", "red"],
	"NLD" : ["red", "white", "blue"],
	"CHE" : ["red", "red", "red"],
	"LTU" : ["yellow", "green", "red"],
	"ITA" : ["green", "white", "red"],
	"GBR" : ["red", "white", "blue"],
<<<<<<< HEAD
=======
	"BEL" : ["black", "yellow", "red"],
>>>>>>> 2319f6dd71bbc5807a0cf119a398acea04db9c75
	"DEU" : ["black", "red", "yellow"],
	"NZL" : ["blue", "blue", "blue"],
	"CZE" : ["white", "blue", "red"],
	"POL" : ["white", "red", "white"],
	"RUS" : ["white", "blue", "red"],
	"SWE" : ["blue", "yellow", "white"],
	"NOR" : ["blue", "red", "red"],
	"ZAF" : ["red", "green", "yellow"],
	"USA" : ["red", "blue", "red"]
	}
	
def fixcoding(addr):
        if addr != None:
                addr=addr.replace(u'á', u'a')
                addr=addr.replace(u'à', u'a')
                addr=addr.replace(u'â', u'a')
                addr=addr.replace(u'Á', u'A')
                addr=addr.replace(u'é', u'e')
                addr=addr.replace(u'è', u'e')
                addr=addr.replace(u'ê', u'e')
                addr=addr.replace(u'É', u'E')
                addr=addr.replace(u'í', u'i')
                addr=addr.replace(u'ì', u'i')
                addr=addr.replace(u'î', u'i')
                addr=addr.replace(u'Í', u'I')
                addr=addr.replace(u'ó', u'o')
                addr=addr.replace(u'ò', u'o')
                addr=addr.replace(u'ô', u'o')
                addr=addr.replace(u'Ó', u'O')
                addr=addr.replace(u'Ò', u'O')
                addr=addr.replace(u'ú', u'u')
                addr=addr.replace(u'ù', u'u')
                addr=addr.replace(u'û', u'u')
                addr=addr.replace(u'Ú', u'U')
                addr=addr.replace(u'ü', u'u')
                addr=addr.replace(u'ñ', u'n')
                addr=addr.replace(u'Ñ', u'N')
                addr=addr.replace(u'Ø', u'O')
        return addr
#-------------------------------------------------------------------------------------------------------------------#

def getflarmid(reg):					# return the flarmId from the registration
	for r in kglid.kglid:				# explore the whole table
		if kglid.kglid[r] == reg:		# if registration is the same
			return ('FLR'+r)		# return the FlarmID
	return ('')
#-------------------------------------------------------------------------------------------------------------------#
#
# arguments:   compid, dayindex, print
#		where compid is the assigned competition ID or 0 for the list of competitions.
#		dayindex is 0 for the first day, 1 second day, etc, ...
#		print is a falg to print the JSON input on pretty print
#

qsgpIDreq=sys.argv[1:]						# first arg is the event ID
dayreq   =sys.argv[2:]						# second arg is the day index within the event
prtreq   =sys.argv[3:]						# print request
 
cucpath=config.cucFileLocation					# directory where to stor the JSON file generated
tp=[]								# turn pint list
tracks=[]							# track list
#

if qsgpIDreq and qsgpIDreq[0] != '0':
	qsgpID   =        sys.argv[1]
	days     =        str(sys.argv[2])
	if days[0].isdigit():	
		day =     int(days)
		days=''
	else:
		day=0
else:
	qsgpID='0'

if prtreq and prtreq[0]=="print":
	prt=True
else:
	prt=False
 
print "Generate .json files V1.1 from  the www.sgp.aero web server"
print "Usage python sgp2sws.py COMPID indexday or http://host/SWS/sgp2sws.html "
hostname=socket.gethostname()
print "DBhost:", config.DBhost, "ServerName:", hostname
start_time = time.time()
local_time = datetime.datetime.now()
j = urllib2.urlopen('http://www.crosscountry.aero/c/sgp/rest/comps/')
j_obj = json.load(j)
if qsgpID == '0':
	#print j_obj
	j=json.dumps(j_obj, indent=4)
	print j
	exit(0)
else:
	for xx in j_obj:
		if xx['id'] == int(qsgpID):
			print "Title:", xx['fullEditionTitle']
	print "CompID:", qsgpID, "Time is now:", local_time     # print the time for information only

fl_date_time = local_time.strftime("%Y%m%d")                    # get the local time
JSONFILE = cucpath + config.Initials + fl_date_time+'.json'     # name of the JSON to be generated
TASKFILE = cucpath + config.Initials + fl_date_time+'.tsk'      # name of the TASK to be generated
COMPFILE = cucpath +'competitiongliders.lst'      		# name of the COMP to be generated
CSVSFILE = cucpath +'competitiongliders.csv'      		# name of the COMP to be generated
print "JSON generated data file is: ", JSONFILE 		# just a trace
print "TASK generated data file is: ", TASKFILE 		# just a trace
print "COMP generated data file is: ", COMPFILE 		# just a trace
print "CSVS generated data file is: ", CSVSFILE 		# just a trace
print "===========================: " 				# just a trace

os.system('rm  '+JSONFILE)		                        # remove the previous one
os.system('rm  '+TASKFILE)		                        # remove the previous one
os.system('rm  '+COMPFILE)		                        # remove the previous one
os.system('rm  '+CSVSFILE)		                        # remove the previous one
jsonfile = open (JSONFILE, 'w')                                 # open the output file
taskfile = open (TASKFILE, 'w')                                 # open the output file
compfile = open (COMPFILE, 'w')                                 # open the output file
csvsfile = open (CSVSFILE, 'w')                                 # open the output file
#
# get the JSON string for the web server
#
j = urllib2.urlopen('http://www.crosscountry.aero/c/sgp/rest/comp/'+str(qsgpID))
j_obj = json.load(j)
if prt:
	#print j_obj
	j=json.dumps(j_obj, indent=4)
	print j
#
# the different pieces of information
#
wlist=[]
clist=[]
flist=[]                                			# Filter list for glidertracker.org
flist.append("ID,CALL,CN,TYPE,INDEX")   			# Initialize with header row
nwarnings=0                                     		# number of warnings ...
warnings=[]                                     		# warnings glider

npil=0								# number of pilots found
pilots=j_obj["p"]						# get the pilot information
print "Pilots:", len(pilots)
print "=========="
for id in pilots:
#                        
	pid= 		pilots[id]["i"] 			# get the pilot ID   
	fname= 		pilots[id]["f"]				# first name    
	lname= 		pilots[id]["l"] 			# last name   
	compid= 	pilots[id]["d"]				# competition number    
	country= 	pilots[id]["z"] 			# two letters country code   
	model= 		pilots[id]["s"]				# aircraft model    
	j= 		pilots[id]["j"]    			# ranking list
	rankingid= 	pilots[id]["r"]				# ranking id
	if int(qsgpID) >= 14:
		flarmid= 	pilots[id]["q"]			# flarm id
		registration= 	pilots[id]["w"]			# registration
		if registration == "":
			print "\nWarning .... Missing glider registration " , flarmid
			nwarnings +=1
			warnings.append(lname) 			# add it to the list of warnings
		flarm = getflarmid(registration)		# get the FlarmId from the registration
		#print "FFF", flarmid, "F", flarm, registration
		if flarmid == '':
			flarmid = getflarmid(registration)	# get the FlarmId from the registration
		if len(flarmid) == 6 and flarmid[0:3] != "FLR":
			flarmid = "FLR"+flarm			# add the FLR assuming Flarm
		if flarm == '':
			flarm = "***NOREG***"
			print "\nWarning .... Flarm not registered on the OGN" , flarmid, flarm
			nwarnings +=1
			warnings.append(lname) 			# add it to the list of warnings

		elif flarmid[3:9] != flarm[3:9]:
			print "\nWarning .... Flarm on system is not the same that Flarms registered on OGN" , flarmid, flarm
			nwarnings +=1
			warnings.append(lname) 			# add it to the list of warnings
	else:
		flarmid= 	"FLRDDDDDD"
		registration= 	"EC-XXX"
	if flarmid != '':
		wlist.append(flarmid[3:9])			# add device to the white list
		clist.append(flarmid)				# add device to the white list
  		flist.append(flarmid+","+registration+","+compid+","+model+","+str(1)) # Populate the filter list
	else:
		warnings.append(lname) 				# add it to the list of warnings
                nwarnings += 1  				# and increase the number of warnings

	#rgb=0x111*int(id)                                       # the the RGB color
    	#ccc=hex(rgb)                                            # convert it to hex
    	#color="#"+ccc[2:]                                       # set the JSON color required
	if hostname == "SWserver":				# deal with the different implementation of pycountry
		ccc = pycountry.countries.get(alpha_2=country)	# the the 3 letter country code
    		country=ccc.alpha_3				# convert to a 3 letter code
	else:
		ccc = pycountry.countries.get(alpha_2=country)	# the the 3 letter country code
    		country=ccc.alpha_3				# convert to a 3 letter code

	color=Flags[country]
	pilotname=fixcoding(fname+" "+lname).encode('utf8')
	print pid, pilotname, compid, country, model, j, rankingid, registration, flarmid, "OGN", flarm[3:9]
	if config.PicPilots == 'FAI':
		tr={"trackId": config.Initials+fl_date_time+":"+flarmid, "pilotName": pilotname,  "competitionId": compid, "country": country, "aircraft": model, "registration": registration, "3dModel": "ventus2", "ribbonColors":color, "portraitUrl": "http://rankingdata.fai.org/PilotImages/"+rankingid+".jpg"}
	else:
		tr={"trackId": config.Initials+fl_date_time+":"+flarmid, "pilotName": pilotname,  "competitionId": compid, "country": country, "aircraft": model, "registration": registration, "3dModel": "ventus2", "ribbonColors":color, "portraitUrl": config.SWSserver+"SWS/pic/"+compid+".png", "3dModelVariant": config.SWSserver+"SWS/pic/"+compid+".sponsor.png"}
	tracks.append(tr)                                       # add it to the tracks
	npil += 1						# increase the number of pilots

#print tracks
print "Wlist:",wlist
print "=========="
print "Competition"
print "==========="
comp=j_obj["c"]							# get the competition information
comp_firstday		=comp['a']				# first day of the competition
comp_lastday		=comp['b']				# last day of the competition
comp_name		=comp['t']				# event name
comp_shortname		=comp['l']				# event short name
comp_id			=comp['i']
print "Comp ID:", comp_id, "Name:", comp_name, "Short name:", comp_shortname, comp_firstday, comp_lastday
numberofactivedays	= 0

if 	j_obj.get ("j") != None :
	numberofactivedays	=j_obj["j"]
if 	j_obj.get ("i") == None :				# check if is fully setup the web site
	print "No index of days ... exiting."
	print "WARNING: No valid JSON file generated ....................."
	exit(-1)
indexofdays		=j_obj["i"]
#print "Index of Days", indexofdays
if days != '':
	cday=0 
	for dayday in indexofdays:
		#print "DAYDAY", days, dayday
		if dayday["l"].upper() == days.upper():
			day = cday
			break
		else:
			cday += 1
			continue
	
date			=indexofdays[day]["d"]			# date    
title			=indexofdays[day]["t"] 			# day tittle   
shorttitle		=indexofdays[day]["l"]    		# day short title
starttime		=indexofdays[day]["a"]    		# start time millis from midnite
daytype			=indexofdays[day]["y"]    		# day type: 1, 2, 3 ...
dayid			=indexofdays[day]["i"] 			# day ID 
print "DATE:", date, "Title:", title, "Day:", shorttitle,"==>", day, "\nStart time(millis):", starttime, "Day type:", daytype, "Day ID:", dayid, "Number of active days:", numberofactivedays


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
	os.system('rm  '+JSONFILE)		                        # remove the previous one
	os.system('rm  '+TASKFILE)		                        # remove the previous one
	exit()
task_type   		=comp_taskinfo["@type"]
task_id  	    	=comp_taskinfo["id"]
task_listid 		=comp_taskinfo["taskListId"]
task_name   		=comp_taskinfo["name"]
task_data   		=comp_taskinfo["data"]
task_creator		=comp_taskinfo["creator"]		# creator
task_description	=comp_taskinfo["description"]		# description of the task
task_desc		=json.loads(task_description) 
task_length		=task_desc["d"]				# task length
task_atfrom		=task_desc["ta"]			# task from

task_at     		=task_data["at"]	
task_wp     		=task_data["g"]	
task_wpla   		=task_data["u"]
task_wptlist		=task_wpla["wptList"]	
task_at_country		=task_at["c"]
task_at_timezone	=task_at["z"]
task_at_elevation	=task_at["e"]
task_at_place		=task_at["n"]
task_at_altitude	=task_at["e"]
task_at_runwaydir	=task_at["d"]
task_at_runwaywidth	=task_at["w"]
task_at_runwaysurface	=task_at["f"]
task_at_runway		=task_at["f"]
task_at_runways		=task_at["k"]
if 	task_at.get ("j") != None :
	task_at_icao	=task_at["j"]
else:
	task_at_icao	="NOID"

task_at_source		=task_at["s"]

if 	task_at.get ("q") != None :
	task_at_freq	=task_at["q"]
else:
	task_at_freq	=0

print "Task info"
print "========="
print "Tasks type:", task_type, "ID:", task_id, task_listid, "Task Name:", task_name 
#print "Task at:", task_at, "WPLA", task_wpla
print "Task country:", task_at_country,"at", task_at_place, "TZ:", task_at_timezone, "Elevation:", task_at_elevation, "Task Runway:", task_at_runway, task_at_runways, task_at_runwaydir, task_at_runwaywidth, task_at_runwaysurface, "Freq:", task_at_freq, "ICAO code:", task_at_icao
print "Task creator:", task_creator, "\nTask length:", task_length, "From:", task_atfrom
print "Number of WP#:", len(task_wp)
print "Waypoints of the task"
print "====================="
#
wp=0
legs=[]
while wp < len(task_wp):
		wp_name				=task_wp[wp]["n"]	# waypoint name
		wp_name 			= "TP"+str(wp)+"-"+wp_name
		if wp == 0:
			wpinit=wp_name
			type="Start"
			wp_name = "START"
		else:
			type="Turnpoint"
		wp_lat				=task_wp[wp]["a"]	# latitude
		wp_lon				=task_wp[wp]["o"]	# longitude
		wp_type				=task_wp[wp]["y"]	# type: line or cylinder
		wp_radius			=task_wp[wp]["r"]	# cylinder radius or line length
		if wp > 0 and  (wp_name == wpinit or wp_type=="line"):
			isbreak=True
			type="Finish"
		if wp_type == "cylinder":
			oz="Cylinder"
		else:
			oz="Line"	
		#wp_id				=task_wp[wp]["id"]	# Wyapoint ID
		if   type == "Start":
			tptexture=config.SWSserver+"SWS/tptextures/START.png"
		elif type == "Finish":
			tptexture=config.SWSserver+"SWS/tptextures/FINISH.png"
			wp_name = "FINISH"
		else:
			tptexture=config.SWSserver+"SWS/tptextures/TP"+str(wp)+".png"
		print "WP:", wp_name, wp_lat, wp_lon,  wp_type, wp_radius, type, oz, tptexture
		tpx={"latitude": wp_lat, "longitude": wp_lon, "name": wp_name, "observationZone": oz, "type": type, "radius": wp_radius, "trigger":"Enter", "texture": tptexture} 
        	tp.append(tpx)
		tlegs=[wp_lat,wp_lon]
		legs.append(tlegs)
		trad=[wp_radius]
		legs.append(trad)
		if wp > 0 and  (wp_name == wpinit or wp_type=="line"):
			break
		wp +=1

print "WP:================================>"
# event

print "Comp short name:", comp_shortname
print "Comp full  name:", comp_name
print "Comp date:", comp_date
print "Comp Start time:", comp_starttime/1000
#print tp
task={ "taskType": "SailplaneGrandPrix", "taskName":"SGPrace", "startOpenTs": comp_date , "turnpoints": tp}
event={"name": comp_shortname, "description" : comp_name, "task" : task , "tracks" : tracks}
j=json.dumps(event, indent=4)
jsonfile.write(j)
print "Task end:==========================>"
print "Generate TSK file ..."
tsk={"name":"SGPrace", "color": "0000FF", "legs":legs, "wlist":wlist}
tsks=[]
tsks.append(tsk)
tasks={"tasks":tsks}
j=json.dumps(tasks, indent=4)                   # dump it
#print j
taskfile.write(j)                               # write it into the task file on json format
j=json.dumps(clist, indent=4)                   # dump it
#print j
compfile.write(j)                               # write it into the comp file on json format

#
# close the files and exit
#

jsonfile.close()
taskfile.close()
os.chmod(TASKFILE, 0o777)                       # make the TASK file accessible
os.chmod(JSONFILE, 0o777)                       # make the JSON file accessible
latest=cucpath+config.Initials+'/SGPrace-latest.tsk'     # the latest TASK file to be used on live.glidernet.org
print "Linking:", TASKFILE+' ==>  '+latest      # print is as a reference
os.system('rm  '+latest)                        # remove the previous one
try:
	os.system('ln -s '+TASKFILE+' '+latest) # link the recently generated file now to be the latest !!!
except:
		print "No latest file ...: ", latest
os.system("gist -login")
cmd="gist -u bd0ebff6b31246570fa31b2df6b701c7 "+latest
#cmd="gist  "+latest
print cmd
try:
	os.system(cmd)
except:
	print "Error on gisy ...: ", cmd
html="https://gist.githubusercontent.com/acasadoalonso/bd0ebff6b31246570fa31b2df6b701c7/raw"
print "Use: "+html
# Write a csv file of all gliders to be used as filter file for glidertracker.org
for item in flist:
                        csvsfile.write("%s\n" % item)
if npil == 0:
        print "JSON invalid: No pilots found ... "
        exit(-1)
else:
        print "Pilots found ... ", npil, "Warnings:", nwarnings
        if nwarnings > 0:
                print "Pilots with no FLARMID: ", warnings
        exit(0)


