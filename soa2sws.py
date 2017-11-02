#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import json
import urllib2
import base64
import datetime
import time
import hmac
import hashlib
import base64
import OpenSSL
import uritemplate
import pycountry
import sqlite3
import MySQLdb
import math
import os
import config

from simplehal import HalDocument, Resolver
from pprint import pprint

#-------------------------------------------------------------------------------------------------------------------#

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


##################################################################
def getapidata(url, auth):                      # get the data from the API server

	
	req = urllib2.Request(url)                      
	req.add_header('Authorization', auth)   # build the authorization header
	req.add_header("Accept","application/json")
	req.add_header("Content-Type","application/hal+json")
	r = urllib2.urlopen(req)                # open the url resource
	j_obj = json.load(r)                    # convert to JSON
	return j_obj                            # return the JSON object

###################################################################

def gdata (url, key, prt='no'):                 # get the data from the soaring spot and return it as a HAL document
        global auth                             # auth and apiurl are globals 
        global apiurl 
        j_obj = getapidata(url, auth)           # call the fuction that get it
                                                # convert to HAL
        if prt == 'yes':                        # if print is required 
                print json.dumps(j_obj, indent=4)
        cd=HalDocument.get_data(HalDocument.from_python(j_obj), apiurl+'rel/' + key) # get the data from the HAL document
        return cd
def getemb (base,ctype):
        global apiurl
        return(base['_embedded'][apiurl+'rel/'+ctype])
        
def getlinks (base, ctype):
        global apiurl
        return (base['_links'] [apiurl+'rel/'+ctype]['href'])


###################################################################

day=sys.argv[1:]                                # see if index day is requestedd        
if day and day[0].isdigit():                    # if provided and numeric
        idx=int(day[0])                         # index day 
else:
        idx=0
clsreq=sys.argv[2:]                             # if class is requested
if clsreq:
        classreq=clsreq[0]                      # class requested
else:
        classreq=' '                            # none        
# ---------------------------------------------------------------- #
print "Util to get the api.soaringspot.com data and convert it to a JSON file compatible with the Silent Wings specs V1.1"
print "==================================================================================================================\n\n"
print "Index day: ", idx, "Class requested: ", classreq
print "Reading data from clientid/secretkey files"
# ===== SETUP parameters =======================#                                          
SWdbpath = config.DBpath                        # where to find the SQLITE3 database
initials = config.Initials			# initials of the files generated
cwd=os.getcwd()					# get the current working directory
cucpath=config.cucFileLocation                  # where to store the JSON files
secpath=cwd+"/SoaringSpot/"                     # where to find the clientid and secretkey files 
apiurl="http://api.soaringspot.com/"            # soaringspot API URL
rel="v1"                                        # we use API version 1
taskType= "SailplaneRacing"                     # race type
# ==============================================#
tsks = {}					# task file

start_time = time.time()                        # get the time now
utc = datetime.datetime.utcnow()                # the UTC time
print "UTC Time is now:", utc  	                # print the time for information only
date = utc.strftime("%Y-%m-%dT%H:%M:%SZ")       # get the local time
print date                                      #

local_time = datetime.datetime.now()            # the local time
print "Local Time is now:", local_time		# print the time for information only
fl_date_time = local_time.strftime("%Y%m%d")	# get the local time

if (config.MySQL):
        connG=MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpasswd, db=config.DBname)     # connect with the database
	print "Config:", config.DBhost, config.DBuser, config.DBname
else:
	connG=sqlite3.connect(SWdbpath+config.SQLite3)	# open the DB with all the GLIDERS information

cursG=connG.cursor()				# cursor for the GLIDERS table

nonce=base64.b64encode(OpenSSL.rand.bytes(36))  # get the once base
f=open(secpath+"clientid")                      # open the file with the client id
client=f.read()                                 # read it
client=client.rstrip()                          # clear the whitespace at the end
f=open(secpath+"secretkey")                     # open the file with the secret key
secretkey=f.read()                              # read it
secretkey=secretkey.rstrip()                    # clear the whitespace at the end
message=nonce+date+client                       # build the message
digest = hmac.new(secretkey, msg=message, digestmod=hashlib.sha256).digest() # and the message digest
signature = base64.b64encode(digest).decode()   # build the digital signature
                                                # the AUTHORIZATION ID is built now   
auth=apiurl+rel+'/hmac/v1 ClientID="'+client+'",Signature="'+signature+'",Nonce="'+nonce+'",Created="'+date+'" ' 

url1=apiurl+rel                                 # get the initial base of the tree 
cd=gdata(url1, 'contests', prt='no')[0]         # get the contest data, first instance

category        =cd['category']
eventname       =cd['name']
compid          =cd['id']
country         =cd['country']                  # country code - 2 chars code
ccc             =pycountry.countries.get(alpha_2=country) # convert the 2 chars ID to the 3 chars ID
country3        =ccc.alpha_3
endate          =cd['end_date']
lc              =getemb(cd,'location')          # location data 
lcname          =lc['name']                     # location name

print "= Contest ==============================="
print "Category:", category,"Comp name:", eventname, "Comp ID:", compid
print "Loc Name:", lcname,   "Country: ", country, country3, "End date:",  endate
print "========================================="

npil=0                                          # init the number of pilots
nwarnings=0                                     # number of warnings ...
warnings=[]                                     # warnings glider

# Build the tracks and turn points, exploring the contestants and task within each class
                                                # go thru the different classes now within the day
for cl in getemb(cd,'classes'):
                                                # search for each class
	tracks=[]				# create the instance for the tracks 
	tp=[]					# create the instance for the turn points
	npilc=0                                 # number of pilot per class
	category        =cl['category']         # category: glider/motorglider/paragliding 
	classtype       =cl['type']             # type: club/open/...
	if classreq != "all":
		if classreq != ' ' and classtype != classreq: # if a class in particular is requested and it is not this one
			continue                # try next one
	classid         =cl['id']               # internal ID of the class
	JSONFILE = cucpath + initials + fl_date_time+"-"+classtype+".json"
	TASKFILE = cucpath + initials + fl_date_time+"-"+classtype+".tsk"
						# name of the JSON to be generated, one per class

	os.system('rm  '+JSONFILE)		# delete the JSON & TASK files
	os.system('rm  '+TASKFILE)
	print "JSON generated data file for the class is: ",JSONFILE # just a trace
	print "TASK generated data file for the class is: ",TASKFILE # just a trace
	print "\n= Class = Category:", category,"Type:", classtype, "Class ID:", classid
	jsonfile = open (JSONFILE, 'w')		# open the output file, one per class 
	taskfile = open (TASKFILE, 'w')		# open the output file, one per class 
	url3=getlinks(cl, "contestants")        # search for the contestants on each class
	ctt=gdata(url3,   "contestants")        # get the contestants data
	print "= Contestants for the class ==========================="
	wlist=[]
	flist=[]				# Filter list for glidertracker.org
	flist.append("ID,CALL,CN,TYPE,INDEX")	# Initialize with header row
	for  contestants in ctt:                # inspect the data of each contestant 
		npil  += 1                      # increase the number of total pilots
		npilc += 1                      # increase the number of pilot within this class
		idflarm=' '                     # no FALRM id yet
		fr=' '                          # no FR yet
		fname=getemb(contestants,'pilot')[0]['first_name']
		lname=getemb(contestants,'pilot')[0]['last_name']
		pname=fixcoding(fname+" "+lname).encode('utf8')  # convert it to utf8 in order to avoid problems 
		if 'aircraft_registration' in contestants:
			regi=contestants['aircraft_registration']
			ff=False                # assume false initially 
			idflarm=' '
			cursG.execute("select * from GLIDERS where registration ='%s'; " % regi)
			for rowg in cursG.fetchall(): # look for that registration on the OGN database 
				#print "\t\t", rowg[0], "For:", rowg[1], rowg[2], rowg[3], rowg[4], rowg[5]
				source=rowg[4]
				devicetype=rowg[5]
				deviceID=rowg[0]
				if idflarm != ' ' and source == 'F':
					continue
				if devicetype == 'F':
					if deviceID[0].isdigit():
						print "Warning: flarmid numeric ...", deviceID
					idflarm="FLR"+rowg[0] # prepend FLR in order to be consistent
				elif devicetype == 'O':
					idflarm="OGN"+rowg[0] # prepend OGN in order to be consistent
				elif devicetype == 'I':
					idflarm="ICA"+rowg[0] # prepend ICA in order to be consistent
				else :
					idflarm="RDN"+rowg[0] # prepend FLR in order to be consistent        
				ff=True         # mark that at least we found one 

			if not ff:
				idflarm=' '     # if not found mark it as blank        

		else:
			regi="reg_NOTYET"      # if we do not have the registration ID on the soaringspot 
			idflarm=' '

		if 'flight_recorders' in contestants:
			fr=contestants['flight_recorders']
			fr=fr.rstrip('\n')
			fr=fr.rstrip('\r')
		else:
			if idflarm != ' ':
				fr=idflarm
			else:
				fr="fr_NOTYET"+str(npil)
				warnings.append(pname) # add it to the list of warnings
				nwarnings += 1  # and increase the number of warnings

		if 'handicap' in contestants:
			hd=contestants['handicap']
		else:
			hd="hd_NOTYET"
		if 'club' in contestants:
			club=fixcoding(contestants['club'])
		else:
			club="club_NOTYET"
		if 'aircraft_model' in contestants:
			ar=contestants['aircraft_model']
		else:
			ar="am_NOTYET"
		if 'contestant_number' in contestants:
			cn=contestants['contestant_number']
		else:
			cn="cn_NOTYET"

		rgb=0x111*npil			        # the the RGB color
		ccc=hex(rgb)			        # convert it to hex
		color="#"+ccc[2:]		        # set the JSON color required

		if 'nationality' in getemb(contestants,'pilot')[0]:
			nation     =getemb(contestants,'pilot')[0]['nationality']
		else:
			nation="ES"                     # by default is SPAIN
		if 'email'       in getemb(contestants,'pilot')[0]:
			email      =getemb(contestants,'pilot')[0]['email']
		else:
			email="email_NOTYET"
		igcid=getemb(contestants,'pilot')[0]['igc_id']
		ccc     = pycountry.countries.get(alpha_2=nation) # convert the 2 char ISO code to 3 chars ISO code
		country = ccc.alpha_3
		if fr[3:9] != 'NOTYET':
			wlist.append(fr[3:9])
			flist.append(fr+","+regi+","+cn+","+ar+","+str(hd)) # Populate the filter list

		# print following infomration: first name, last name, Nation, Nationality, AC registration, call name, flight recorder ID, handicap aircraft model, club, IGC ID
		print "\t", fname+" "+lname, nation, country, regi, cn, fr, hd, ar, club, igcid 
		if idflarm==' ':
			idflarm=str(npil)
							# create the track
		if igcid != 0:					
			tr={"trackId": initials+fl_date_time+":"+idflarm, "pilotName": pname,  "competitionId": cn, "country": country,\
			    "aircraft": ar, "registration": regi, "3dModel": "ventus2", "ribbonColors":[color],\
			    "portraitUrl": "http://rankingdata.fai.org/PilotImages/"+str(igcid)+".jpg"}
		else:        
			tr={"trackId": initials+fl_date_time+":"+idflarm, "pilotName": pname,  "competitionId": cn, "country": country,\
			    "aircraft": ar, "registration": regi, "3dModel": "ventus2", "ribbonColors":[color]}
		tracks.append(tr)			# add it to the tracks

	url4=getlinks(cl, "tasks")                      # look for the tasks within that class 
	ctt=gdata(url4,   "tasks")                      # get the TASKS data for the day
	print "= Tasks ==", ctt[idx]["task_date"]
	print "= Tasks ==", ctt[idx]["result_status"]
	print "= Tasks ==", ctt[idx]["task_distance"]/1000
	print "= Tasks ==", "Kms.", ctt[idx]["task_type"]
	
	url5=getlinks(ctt[idx],"points")                # look for the waypoints within the task 
	cpp=gdata(url5,        "points")                # look for the waypoints within the task within the day IDX
	print "= Waypoints for the task within the class  ============"
	tasklen=0                                       # task length for double check 
	ntp=0
	legs=[]						# legs for the task file
	for point in cpp:                               # search for each waypoint within the task 
		lati= point["latitude"]
		long= point["longitude"]
		alti= point["elevation"]
		lati= math.degrees(lati)                # the latitude is in radians, convert to GMS
		long= math.degrees(long)
		wtyp= point["type"]                     # waypoint type start/point/finish
		name= fixcoding(point["name"])          # waypoint name
		pidx= point["point_index"]              # waypoint number within the task
		ozty= point["oz_type"];			# oz type: next/symmetric/previous
		ozra= point["oz_radius1"];		# oz radius
		ozr2= point["oz_radius2"];		# oz radius
		dist= point["distance"]/1000;		# distance in kms.
		if ozr2 <= 0:
			ozr2=500

		if   (wtyp == "start"):                 # convert from CU format to SW format
			type="Start"
			oz  ="Line"
			rad=ozra
			dist=0
		elif (wtyp == "finish"):
			type="Finish"
			oz  ="Cylinder"
			rad=ozra
		else:
			type="Turnpoint"
			oz  ="Cylinder"
			rad=ozr2

		print "\t", name, wtyp, type, oz, lati, long, alti, dist, ozty, ozra, ozr2, oz, type, rad, pidx        # print it as a reference
							# built the turning point 
		tpx={"latitude": lati, "longitude": long, "name": name, "observationZone": oz, "type": type, "radius": rad, "trigger":"Enter"}
		tp.append(tpx)                          # add it to the TP
		tlegs=[lati,long]
		legs.append(tlegs)
		trad=[rad]
		legs.append(trad)
		ntp +=1					# number of TPs 
		tasklen += dist                         # compute the task distance

	print "=Task length: ", tasklen, "Number of pilots in the class: ", npilc # just a control of the total task distance

	tps=[]						# create the instance for the turn points
	while ntp > 0:					# reverse the order of the TPs
		ntp -=1
		tps.append(tp[ntp])
	local_time = datetime.datetime.utcnow()         # the local time
							# build the event
# event
        y=local_time.year
        m=local_time.month
        d=local_time.day
        td=datetime.datetime(y,m,d)-datetime.datetime(1970,1,1)         # number of second until beginning of the day
        ts=int(td.total_seconds()+9*60*60)                              # timestamp 09:00:00 UTC
	event={"name": classtype+"-"+eventname, "description" : classtype,  "eventRevision": 0, "task" : { "taskName": classtype, "taskType": taskType, "startOpenTs": ts, "turnpoints": tps },  "tracks": tracks}

	j=json.dumps(event, indent=4)                   # dump it
	jsonfile.write(j)                               # write it into the JSON file
	jsonfile.close()                                # close the JSON file for this class
        os.chmod(JSONFILE, 0o777) 			# make the JSON file accessible  
	#print j
	print "Generate TSK file ..."
	tsk={"name":classtype, "color": "0000FF", "legs":legs, "wlist":wlist}
	tsks=[]
	tsks.append(tsk)
	tasks={"tasks":tsks}
	j=json.dumps(tasks, indent=4)                   # dump it
	#print j
	taskfile.write(j)                               # write it into the task file on json format
	taskfile.close()                                # close the TASK file for this class
        os.chmod(TASKFILE, 0o777) 			# make the TASK file accessible
	latest=cucpath+initials+'/'+classtype+'-latest.tsk'	# files that contains the latest TASK file to be used on live.glidernet.org 
	print TASKFILE+' ==>  '+latest			# print is as a reference
	try:
		os.system('rm  '+latest)		# remove the previous one
	except:
		print "No previous task file"
	os.link(TASKFILE, latest)			# link the recently generated file now to be the latest !!!

        # html="https://gist.githubusercontent.com/acasadoalonso/90d7523bfc9f0d2ee3d19b11257b9971/raw"
        # cmd="gist -u 90d7523bfc9f0d2ee3d19b11257b9971 "+TASKFILE
        cmd="gist "+TASKFILE+" > /home/pi/SWdata/gist.log"
	# print cmd
        os.system(cmd)
	# print "Use: "+html

	# Write a csv file of all gliders to be used as filter file for glidertracker.org
	with open(cucpath + initials + fl_date_time+"-"+classtype+"filter.csv", 'wb') as myfile:
		for item in flist:
			myfile.write("%s\n" % item)


print "= Pilots ===========================", npil      # print the number of pilots as a reference and control


connG.close()                                           # close the connection

if npil == 0:
	print "JSON invalid: No pilots found ... "
	exit(-1)
else:
	print "Pilots found ... ", npil, "Warnings:", nwarnings
	if nwarnings > 0:
		print "Pilots with no FLARMID: ", warnings
	exit(0)
