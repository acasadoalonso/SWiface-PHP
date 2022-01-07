#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
import json
import urllib.request, urllib.error, urllib.parse
import base64
import datetime
import time
import hmac
import hashlib
import base64
#import OpenSSL
#import uritemplate
import pycountry
import math
import os
import socket
import config
import geopy
from stat import *
from ognddbfuncs import *
from geofuncs import convertline 
from uritemplate import expand
from copy import deepcopy
try:
   from simplehal import HalDocument, Resolver
except ImportError:
   cwd = os.getcwd()
   print("import error... ",cwd)
   #sys.path.insert(0, cwd)
   from simplehal import HalDocument, Resolver

from geopy.distance import geodesic     # use the geodesic (Vincenty deprecated) algorithm^M
from gistfuncs import *


#-------------------------------------------------------------------------------------------------------------------#


##################################################################


def getapidata(url, auth):                  # get the data from the API server

    req = urllib.request.Request(url)
    req.add_header('Authorization', auth)   # build the authorization header
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/hal+json")
    r = urllib.request.urlopen(req)         # open the url resource
    rr=r.read().decode('UTF-8')             # convert to JSON
    j_obj = json.loads(rr)

    return j_obj                            # return the JSON object

###################################################################


                                            # get the data from the soaring spot and return it as a HAL document
def gdata(url, key, prt='no'):
    global auth                             # auth and apiurl are globals
    global apiurl
    j_obj = getapidata(url, auth)           # call the fuction that get it
                                            # convert to HAL
    if prt == 'yes':                        # if print is required
        print(json.dumps(j_obj, indent=4))
    cd = HalDocument.get_data(HalDocument.from_python(
        j_obj), apiurl+'rel/' + key)        # get the data from the HAL document
    return cd


def getemb(base, ctype):
    global apiurl
    return(base['_embedded'][apiurl+'rel/'+ctype])


def getlinks(base, ctype):
    global apiurl
    return (base['_links'][apiurl+'rel/'+ctype]['href'])


###################################################################

# see if index day is requestedd
day = sys.argv[1:]
if day and day[0].isdigit():                    # if provided and numeric
    idx = int(day[0])                           # index day
else:
    idx = 0
clsreq = sys.argv[2:]                           # if class is requested
if clsreq:
    classreq = clsreq[0]                        # class requested
    print("TTT", classreq)
else:
    classreq = ' '                              # none


version='V2.03'
# ---------------------------------------------------------------- #
print("\n\nUtility to get the api.soaringspot.com data and convert it to a JSON file compatible with the Silent Wings specs Version: "+version)
print("=================================================================================================================================\n\n")
print("Index day: ", idx, " Class requested: ", classreq)
print("Reading data from clientid/secretkey files")
# ===== SETUP parameters =======================#
                                                # where to find the SQLITE3 database
SWdbpath = config.DBpath
if not os.path.isdir(SWdbpath):
   SWdbpath='.'
initials = config.Initials		        # initials of the files generated
if 'USER' in os.environ:
        user=os.environ['USER']
else:
        user="www-data"                     # assume www
if 'APACHE_RUN_USER' in os.environ or user == "www-data":        # check if www
        www=True
else:
        www=False
cwd = os.getcwd()				# get the current working directory
                                                # where to store the JSON files
cucpath = config.cucFileLocation
if not os.path.isdir(cucpath):
   cucpath='./'
if os.path.isdir(cucpath+initials):
   mode = os.stat(cucpath+initials).st_mode
   if not (mode & S_IWOTH or mode & S_IWGRP):
       print("Check permisions on:", cucpath+initials, filemode(mode), "%o"%mode)
else:
   print("Check directory:", cucpath+initials)
locname =config.locname
                                                # where to find the clientid and secretkey files
secpath  = cwd+"/SoaringSpot/"
apiurl   = "http://api.soaringspot.com/"        # soaringspot API URL
rel      = "v1"                                 # we use API version 1
taskType = "SailplaneRacing"                    # race type

# ==============================================#
tsks = {}					# task file
hostname = socket.gethostname()			# hostname as control
print("Hostname:", hostname, "User:", user, " WWW:", www)
start_time = time.time()                        # get the time now
utc = datetime.datetime.utcnow()                # the UTC time
                                                # print the time for information only
print("UTC Time is now:", utc)
date = utc.strftime("%Y-%m-%dT%H:%M:%SZ")       # get the local time
print(date)                                     #

local_time = datetime.datetime.now()            # the local time
print("Local Time is now:", local_time)		# print the time for information only
fl_date_time = local_time.strftime("%Y%m%d")    # get the local time
td_date_time = local_time.strftime("%Y-%m-%d")  # get the local time
print("Config params. SWpath: ", SWdbpath, ", Initials:", initials, ", Location Name:", locname, ", CUCpath:", cucpath)

nonce = base64.b64encode(os.urandom(36))        # get the once base
                                                # open the file with the client id
f = open(secpath+"clientid")
client = f.read()                               # read it
                                                # clear the whitespace at the end
client = client.rstrip()
                                                # open the file with the secret key
f = open(secpath+"secretkey")
secretkey = f.read()                            # read it
                                                # clear the whitespace at the end
secretkey = secretkey.rstrip().encode(encoding='utf-8')
message = nonce+date.encode(encoding='utf-8')+client.encode(encoding='utf-8')   # build the message
                                                # and the message digest
digest = hmac.new(secretkey, msg=message, digestmod=hashlib.sha256).digest()
signature = str(base64.b64encode(digest).decode())   # build the digital signature
                                                # the AUTHORIZATION ID is built now

auth = apiurl+rel+'/hmac/v1 ClientID="'+client+'",Signature="' + \
    signature+'",Nonce="'+nonce.decode(encoding='utf-8')+'",Created="'+date+'" '
#print ("URLiauth:", auth)

                                                # get the initial base of the tree
url1 = apiurl+rel
                                                # get the contest data, first instance
cd = gdata(url1, 'contests', prt='no')[0]

#ogndata=getddbdata()                            # get the OGB DDB
category = cd['category']
eventname = cd['name']
compid = cd['id']
country = cd['country']                         # country code - 2 chars code
compcountry = country				# contry as defaults for pilots
                                                # convert the 2 chars ID to the 3 chars ID
ccc = pycountry.countries.get(alpha_2=country)
country3 = ccc.alpha_3
endate = cd['end_date']
lc = getemb(cd, 'location')                     # location data
lcname = lc['name']                             # location name

print("= Contest ===============================")
print("Category:", category, "Comp Name:", eventname, "Comp ID:", compid)
try:
   print("Loc Name:", lcname.encode('utf-8').decode('utf-8') ,   "Country: ", country, country3, "End date:",  endate)
except:
   print( "Country: ", country, country3, "End date:",  endate)
   
print("=========================================")

npil = 0                                        # init the number of pilots
nwarnings = 0                                   # number of warnings ...
warnings = []                                   # warnings glider
filenames=False

# Build the tracks and turn points, exploring the contestants and task within each class
# go thru the different classes now within the day

for cl in getemb(cd, 'classes'):
                                                # search for each class
    tracks = []				        # create the instance for the tracks
    tp = []					# create the instance for the turn points
    npilc = 0                                   # number of pilot per class
                                                # category: glider/motorglider/paragliding
    category = cl['category']
    classtype = cl['type']                      # type: club/open/...
    if classreq != "all":
                                                # if a class in particular is requested and it is not this one
        if classreq != ' ' and classtype != classreq:
            continue                            # try next one
    classid = cl['id']                          # internal ID of the class
    JSONFILE = cucpath + initials + fl_date_time+"-"+classtype+".json"
    TASKFILE = cucpath + initials + fl_date_time+"-"+classtype+".tsk"
    CSVFILE  = cucpath + initials + fl_date_time+"-"+classtype+"_filter.csv"
    COMPFILE = cucpath + initials + fl_date_time+"-"+classtype+"_competitiongliders.lst"
                                                # name of the JSON to be generated, one per class
    if os.path.isfile(JSONFILE):
    	os.system('rm  '+JSONFILE)		# delete the JSON & TASK files
    if os.path.isfile(TASKFILE):
        os.system('rm  '+TASKFILE)
    if os.path.isfile(CSVFILE):
        os.system('rm  '+CSVFILE)
    if os.path.isfile(COMPFILE):
        os.system('rm  '+COMPFILE)
    print("JSON generated data file for the class is: ", JSONFILE)  # just a trace
    print("TASK generated data file for the class is: ", TASKFILE)  # just a trace
    print("CSV  generated data file for the class is: ", CSVFILE)   # just a trace
    print("COMP generated data file for the class is: ", COMPFILE)  # just a trace

    print("\n= Class = Category:", category, "Type:", classtype, "Class ID:", classid)
    jsonfile = open(JSONFILE, 'w')		# open the output file, one per class
    taskfile = open(TASKFILE, 'w')		# open the output file, one per class
    csvfile  = open(CSVFILE,  'w')		# open the output file, one per class
    compfile = open(COMPFILE, 'w')		# open the output file, one per class
    filenames=True				# set a mark that we created the files
#   --------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    						# PILOTS within the CLASS
                                                # search for the contestants on each class
    url3 = getlinks(cl, "contestants")
    ctt  = gdata(url3,  "contestants")          # get the contestants data
    print("= Contestants for the class ===========================")
    wlist  = []				        # filter for live.glidernet.org
    tptype = []				        # set the turning point type
    flist  = []				        # Filter list for glidertracker.orga
    flist.append("ID,CALL,CN,TYPE,INDEX")       # Initialize with header row
    clist  = []				        # list of competitors

    for contestants in ctt:                     # inspect the data of each contestant
        npil += 1                               # increase the number of total pilots
        npilc += 1                              # increase the number of pilot within this class
        idflarm = ' '                           # no FALRM id yet
        idfreg = ' '                            # no FALRM id yet
        ognid = ' '                           	# no OGNID (THE ID from the OGN DDB) yet
        ognpair = ' '                          	# the ogn tracker to be paired
        fr = ' '                                # no FR yet
        fname = getemb(contestants, 'pilot')[0]['first_name']
        lname = getemb(contestants, 'pilot')[0]['last_name']
                                                # convert it to utf8 in order to avoid problems
        pname = (fname+" "+lname).encode('utf-8').decode('utf-8')
        if 'live_track_id' in contestants:      # check if we have the FlarmId from the SoaringSpot
            livetrk = contestants['live_track_id']  # flarmID and OGN pair
            if len(livetrk) == 9:
               idflarm = livetrk		# case that just the FlarmID, no piaring
            if len(livetrk) == 19:              # format:  FLR123456 OGN654321
               idflarm = livetrk[0:9]		# case that just the FlarmID and OGN tracker pair
               ognpair = livetrk[10:]		# OGN trackers paired
            if len(idflarm) == 6:               # in case of missing FLR/ICA/OGN (deprecated)
                if idflarm[0] == 'D':
                    idflarm="FLR"+idflarm       # assume a Flarm type 
                elif idflarm[0].isdigit():
                    idflarm="ICA"+idflarm       # assume a ICAO type
                else:
                    idflarm="OGN"+idflarm       # assume a OGN type

            idfreg=getognreg(idflarm[3:9]) 	# get the registration from OGN DDB       
            if 'aircraft_registration' in contestants:
                regi = contestants['aircraft_registration']
                ognid=getognflarmid(regi)       # get the flarm if from the OGN DDB
                if (ognid == "NOFlarm"):
                   ognid=getognreg(idflarm[3:9])# show the differences
                   #ognid=getogninfo(idflarm[3:9])# show the differences
            else:
                regi = "reg_NOTYET"             # if we do not have the registration ID on the soaringspota
            
        elif 'aircraft_registration' in contestants:
            regi = contestants['aircraft_registration']
            idflarm=getognflarmid(regi)         # get the flarm if from the OGN DDB
            ognid=idflarm
        else:
            regi = "reg_NOTYET"                 # if we do not have the registration ID on the soaringspot
            idflarm = ' '

        if 'flight_recorders' in contestants:
            fr = contestants['flight_recorders']
            fr = fr.rstrip('\n')
            fr = fr.rstrip('\r')
        else:
            fr = "fr_NOTYET"+str(npil)
        if idflarm == ' ' or idflarm == 'NOREG  ':
            warnings.append(pname)              # add it to the list of warnings
            nwarnings += 1                      # and increase the number of warnings

        if 'handicap' in contestants:
            hd = contestants['handicap']
        else:
            hd = "hd_NOTYET"
        if 'club' in contestants:
            club = contestants['club'].encode('utf-8').decode('utf-8')
        else:
            club = "club_NOTYET"
        if 'aircraft_model' in contestants:
            ar = contestants['aircraft_model']
        else:
            ar = "am_NOTYET"
        if 'contestant_number' in contestants:
            cn = contestants['contestant_number']
        else:
            cn = "cn_NOTYET"

        rgb = 0x111*npil		        # the the RGB color
        ccc = hex(rgb)			        # convert it to hex
        color = "#"+ccc[2:]		        # set the JSON color required

        if 'nationality' in getemb(contestants, 'pilot')[0]:
            nation = getemb(contestants, 'pilot')[0]['nationality']
        else:

            if compcountry != '':
                nation = compcountry
            else:
                nation = "ES"                   # by default is SPAIN
        if 'email' in getemb(contestants, 'pilot')[0]:
            email = getemb(contestants, 'pilot')[0]['email']
        else:
            email = "email_NOTYET"
        igcid = getemb(contestants, 'pilot')[0]['igc_id']
                                                # convert the 2 char ISO code to 3 chars ISO code
        ccc = pycountry.countries.get(alpha_2=nation)
        country = ccc.alpha_3

        if idflarm != 'NOTYET':
            if idflarm != " ":
                wlist.append(idflarm[3:9])
            else:
                print("Missing Flarm:", fname, lname)
            flist.append(idflarm+","+regi+","+cn+","+ar+"," + str(hd))   # Populate the filter lista

        clist.append(idflarm)			# add device to the competion list
        if ognpair != ' ':
           clist.append(ognpair)		# add pairing tracker to the competion list
        else:
           clist.append("OGNFFFFFF")		# add pairing tracker to the competion list

        # print following infomration: first name, last name, Nation, Nationality, AC registration, call name, flight recorder ID, handicap aircraft model, club, IGC ID
        try:
            print("\t", (fname+" "+lname),  nation, country, regi, cn, hd, ar, club, igcid, idflarm, '(Reg:', idfreg, ')', "OGNDDB:==>", ognid, "Pairing with:", ognpair)  # , fr
        except:
            print("\n\t", pname.encode(encoding='utf-8'), nation, country, regi, cn, hd, ar, club.encode(encoding='utf-8'), igcid, idflarm, "OGN DDB:==>", ognid, "Pairing with:", ognpair )  # , fr
        if idflarm == ' ':
            idflarm = str(npil)
                                                # create the track
        if igcid != 0:
            tr = {"trackId": initials+fl_date_time+":"+idflarm, "pilotName": pname,  "competitionId": cn, "country": country,
                  "aircraft": ar, "registration": regi, "3dModel": "ventus2", "ribbonColors": [color],
                  "portraitUrl": "http://rankingdata.fai.org/PilotImages/"+str(igcid)+".jpg"}
        else:
            tr = {"trackId": initials+fl_date_time+":"+idflarm, "pilotName": pname,  "competitionId": cn, "country": country,
                  "aircraft": ar, "registration": regi, "3dModel": "ventus2", "ribbonColors": [color]}
        tracks.append(tr)			# add it to the tracks

    print("= Number of pilots in this class =========================== ", npilc)

#   --------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    						# TASK within the CLASS
                                                # look for the tasks within that class
    url4 = getlinks(cl, "tasks")
                                                # get the TASKS data for the day
    try:
        ctt = gdata(url4,   "tasks")
    except:
        print ("No task yet...", url4)          # when the task is not ready
        os.system('rm  '+JSONFILE)		# delete the JSON & TASK files
        os.system('rm  '+TASKFILE)
        os.system('rm  '+CSVFILE)
        os.system('rm  '+COMPFILE)
        continue				# nothing else to do now
    print("= Tasks ==", ctt[idx]["task_date"])
    if td_date_time != ctt[idx]["task_date"]:
        print ("Warning ... the task date is not today!!!")
        nwarnings += 1
        warnings.append('<< DATE >>--'+classtype)
    print("= Tasks ==", ctt[idx]["result_status"])
    print("= Tasks ==", ctt[idx]["task_distance"]/1000)
    tasktype = ctt[idx]["task_type"]
    print("= Tasks ==", "Kms.  ", tasktype)

#   --------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
                                                # look for the waypoints within the task
    url5 = getlinks(ctt[idx], "points")
                                                # look for the waypoints within the task within the day IDX
    cpp = gdata(url5,        "points")
    print("= Waypoints for the task within the class  ============")
    tasklen = 0                                 # task length for double check
    ntp = 0                                     # number of turning points
    wp = 0
    legs = []					# legs for the task file

    for point in cpp:                           # search for each waypoint within the task
        lati = point["latitude"]
        lon  = point["longitude"]
        alti = point["elevation"]
                                                # the latitude is in radians, convert to GMS
        lati = math.degrees(lati)
        lon  = math.degrees(lon)
                                                # waypoint type start/point/finish
        wtyp = point["type"]
        name = point["name"].encode('utf8').decode('utf8') # waypoint name
                                                # waypoint number within the task
        pidx = point["point_index"]
        ozty = point["oz_type"]			# oz type: next/symmetric/previous
        ozra = point["oz_radius1"]		# oz radius
        ozr2 = point["oz_radius2"]		# oz radius
        dist = point["distance"]/1000		# distance in kms.
        if ozr2 <= 0:
            ozr2 = 500

        if (wtyp == "start"):                   # convert from CU format to SW format
            ttype = "Start"
            oz = "Line"
            rad = ozra
            dist = 0
        elif (wtyp == "finish"):
            ttype = "Finish"
            oz = "Cylinder"
            rad = ozra
        else:
            ttype = "Turnpoint"
            oz = "Cylinder"
            if tasktype == "assigned_area":
                rad = ozra
            else:
                rad = ozr2
        if ttype == "Start":
            tptexture = config.TPTserver+"SWS/tptextures/START.png"
        elif ttype == "Finish":
            tptexture = config.TPTserver+"SWS/tptextures/FINISH.png"
        else:
            tptexture = config.TPTserver+"SWS/tptextures/TP"+str(ntp)+".png"
        try:
                                                # print it as a reference
            print("\t", name, wtyp, ttype, oz, lati, lon, alti, dist, ozty, ozra, ozr2, oz, ttype, rad, pidx, tptexture)
        except:
                                                # print it as a reference
            print("\t",  wtyp, ttype, oz, lati, lon, alti, dist, ozty, ozra, ozr2, oz, ttype, rad, pidx, tptexture)
                                                # built the turning point
        tpx = {"latitude": lati, "longitude": lon, "name": name, "observationZone": oz,
               "type": ttype, "radius": rad, "trigger": "Enter", "texture": tptexture}
        tp.append(tpx)                          # add it to the TP
        tptype.append(oz)                       # save the turning point ype
        tlegs = [lati, lon]                     # legs
        legs.append(tlegs)
        trad = [rad]
        legs.append(trad)
        ntp += 1				# number of TPs
        tasklen += dist                         # compute the task distance
# end of WAYPOINT for
    print("= Number of WayPoints  ============ ", ntp)
                                                # just a control of the total task distance
    print("= Task length: ", tasklen, "Number of pilots in the class: ", npilc)
#   --------------------------------------------------------------------------------------------------------------------------------------------------------------------- #

    tps = []					# create the instance for the turn points
    tpt = []					# create the instance for the turn points
    while ntp > 0:				# reverse the order of the TPs
        ntp -= 1
        tps.append(tp[ntp])
        tpt.append(tptype[ntp])
    local_time = datetime.datetime.utcnow()     # the local time
                                                # build the event
                                                # event
    y = local_time.year
    m = local_time.month
    d = local_time.day
                                                # number of second until beginning of the day
    td = datetime.datetime(y, m, d)-datetime.datetime(1970, 1, 1)
                                                # timestamp 09:00:00 UTC
    ts = int(td.total_seconds()+9*60*60)
    event = {"name": classtype+"-"+eventname, "description": classtype,  "eventRevision": 0, "task": {
        "taskName": classtype, "taskType": taskType, "startOpenTs": ts, "turnpoints": tps},  "tracks": tracks}
    j = json.dumps(event, indent=4)             # dump it
                                                # write it into the JSON file
    jsonfile.write(j)
    jsonfile.close()                            # close the JSON file for this class
    os.chmod(JSONFILE, 0o777) 			# make the JSON file accessible
    #print j
    print("Generate TSK file ...")
    tsk = {"name": classtype, "color": "0000FF", "legs": legs, "TPpointstype": tptype, "wlist": wlist}
    tsks = []
    tsks.append(tsk)
    tasks = {"tasks": tsks}
    tasks = convertline(tasks)                  # convert the START line on 3 point that will draw a line
    t = json.dumps(tasks, indent=4)             # dump the TASK file  .tsk
    #print j
                                                # write it into the task file on json format
    taskfile.write(t)
    taskfile.close()                            # close the TASK file for this class
    os.chmod(TASKFILE, 0o777) 			# make the TASK file accessible
                                                # files that contains the latest TASK file to be used on live.glidernet.org
    latest = cucpath+initials+'/'+classtype+'-latest.tsk'
    print(TASKFILE+' ==>  '+latest)		# print is as a reference
    try:
        if os.path.isfile(latest):
           os.system('rm  '+latest)		# remove the previous one
    except:
        print("No previous task file")
                                                # link the recently generated file now to be the latest !!!
    try:
        os.link(TASKFILE, latest)
    except:
        print("error on link")

    # Write a csv file of all gliders to be used as filter file for glidertracker.org
    try:
        for item in flist:
            csvfile.write("%s\n" % item)
    except:
        print("error on writing CSV file ... ", flist)
    csvfile.close()				# close the CSV file
    os.chmod(CSVFILE, 0o775) 			# make the CSV file accessible

    # Write a comp file of all gliders to be used as filter file for pairing
    j = json.dumps(clist, indent=4)             # dump it
                                                # write it into the comp file on json format
    try:
        compfile.write(j)
        compfile.close()                        # close the COMP file for this class
    except:
        print("error on writing COMP file ... ", clist)

    os.chmod(COMPFILE, 0o775) 			# make the COMP file accessible
    if config.GIST:				# if GIST is requested
       content=t+"\n"				# the content is the TASK file
       res=updategist(config.GIST_USER, classtype+" latest task", config.GIST_TOKEN, TASKFILE, content)
       print ("GIST RC: ", res.status_code)
       if res.status_code == 200 or res.status_code == 201:
          id=res.json()['id']
          print("https://gist.githubusercontent.com/"+config.GIST_USER+"/"+id+"/raw/")
       else:
          print("Error on GIST ....", res.status_code)

# end of CLASSES for 
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- #




# print the number of pilots as a reference and control
print("= Pilots ===========================", npil, "\n\n")



if npil == 0:
    print("JSON invalid: No pilots found ...  or invalid class ...")
    if filenames:
        os.system('rm  '+JSONFILE)		        # delete the JSON & TASK files
        os.system('rm  '+TASKFILE)
        os.system('rm  '+CSVFILE)
    exit(-1)
else:
    print("Pilots found ... ", npil, "Warnings:", nwarnings, "Date & time:", date)
    if nwarnings > 0:
        print("Pilots with no FLARMID or invalid date: ", warnings)
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n\n")
    exit(0)
#   --------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
