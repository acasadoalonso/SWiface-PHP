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
import urllib
import config

from simplehal import HalDocument, Resolver
from pprint import pprint
import hashlib
import base64
import hmac
import urllib
import urllib2
import random

#-------------------------------------------------------------------------------------------------------------------#
def otpReply(question):
        signature = hmac.new(LT24_appSecret, msg=question, digestmod=hashlib.sha256).hexdigest()
        #print signature
        vc=signature[0:16]
        #print vc
        return "/ak/" + LT24_appKey + "/vc/" + vc

def lt24req(cmd):
        global LT24qwe
        lt24req="http://api.livetrack24.com/api/v2/"
        reply=otpReply(LT24qwe)
        lt24url=lt24req+cmd+reply
        f=urllib2.urlopen(lt24url)
        response = f.read()
        qwepos= response.find("qwe")
        LT24qwe=response[qwepos+6:qwepos+22]
        return (response)
#-------------------------------------------------------------------------------------------------------------------#


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

def getLT24tp(tp):
	fd=open("./LT24/lt24tp.txt", "r")
	for line in fd: 
		idx=line[0:2]
		tp[idx]=line[3:9]
	fd.close()
	return
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
LT24tp={}
LT24date={}
# ---------------------------------------------------------------- #
print "Util to get the api.soaringspot.com data and convert it to a LiveTrack24 API"
print "============================================================================\n\n"
print "Index day: ", idx, "Class requested: ", classreq, "\n\n"
print "Reading data from clientid/secretkey files"
# ===== SETUP parameters =======================#                                          
SWdbpath = config.DBpath                        # where to find the SQLITE3 database
initials = config.Initials			# initials of the files generated
cucpath=config.cucFileLocation                  # where to store the JSON files
secpath="./SoaringSpot/"                        # where to find the clientid and secretkey files 
LT24path="./LT24/"                              # where to find the clientid and secretkey files 
apiurl="http://api.soaringspot.com/"            # soaringspot API URL
rel="v1"                                        # we use API version 1
taskType= "SailplaneRacing"                     # race type
# ==============================================#

start_time = time.time()                        # get the time now
utc = datetime.datetime.utcnow()                # the UTC time
print "UTC Time is now:", utc  	                # print the time for information only
date = utc.strftime("%Y-%m-%dT%H:%M:%SZ")       # get the local time

local_time = datetime.datetime.now()            # the local time
print "Local Time is now:", local_time		# print the time for information only
fl_date_time = local_time.strftime("%Y%m%d")	# get the local time

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

#
# LOGIN into Livetract24 and get the list of tasks.
#

getLT24tp   (LT24tp)				# get the LT34 wayoint list
print "\nTotal number of WayPoints on the LT24 file:" , len(LT24tp.keys())
f=open(LT24path+"clientid")                     # open the file with the client id
client=f.read()                                 # read it
LT24_appKey=client.rstrip()                     # clear the whitespace at the end
f=open(LT24path+"secretkey")                    # open the file with the secret key
secretkey=f.read()                              # read it
LT24_appSecret=secretkey.rstrip()               # clear the whitespace at the end
LT24qwe=" "
lt24req("op/ping")				# the first time always is in error but we get the first QWE
replylogin = lt24req("op/6/username/acasado/pass/correo") 
LT24login = json.loads(replylogin)		# parse the JSON string
print "LT24 login:", LT24login['userID'], LT24login['username']
#
# Build the LT24 tasks
#
LT24task2get='36'
if LT24login["error"] == "":
		print "LT24 op/ping", json.loads(lt24req("op/ping"))['ip']
		LT24tasks = json.loads(lt24req("/op/tasksList/tasksToGet/"+LT24task2get))
		#print json.dumps(LT24tasks, indent=4)
		tday={}
		pdate=""
		compname=""
		print "LT24 Days and Task IDs"
		print "======================"
		for td in LT24tasks['tasksList']:
			tdate=td['date']
			compname=td['compName']
			pos=td['taskName'].find(', ')
			tclass=td['taskName'][pos+2:]
			tid=str(td['taskID'])
			#print tclass, tdate, tid, pdate
			if pdate!=tdate and pdate != "":
				LT24date[pdate]=tday
				pdate=tdate
				tday={}
			#print td
			tday[tclass]=tid
			pdate=tdate
		if pdate != "":
			LT24date[pdate]=tday
			tday={}
		for day in LT24date:
			print "Day:", day, "TaskIDs", LT24date[day], compname
		print "\n\n"
	
# --------------------------------------------------------------------------------

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
	print "\n= Class = Category:", category,"Type:", classtype, "Class ID:", classid
	url4=getlinks(cl, "tasks")                      # look for the tasks within that class 
	ctt=gdata(url4,   "tasks")                      # get the TASKS data for the day
	taskdate= ctt[idx]["task_date"]			# the task date
	print "= Tasks ==", ctt[idx]["task_date"], ctt[idx]["result_status"],  ctt[idx]["task_distance"]/1000, "Kms.", ctt[idx]["task_type"]
	
	url5=getlinks(ctt[idx],"points")                # look for the waypoints within the task 
	cpp=gdata(url5,        "points")                # look for the waypoints within the task within the day IDX
	print "= Waypoints for the task within the class  ============"
	tasklen=0                                       # task length for double check 
	ntp=0
	lt24wp=""
	for point in cpp:                               # search for each waypoint within the task 
		wtyp= point["type"]                     # waypoint type start/point/finish
		name= point["name"]                     # waypoint name
		pidx= point["point_index"]              # waypoint number within the task
		ozty= point["oz_type"];			# oz type: next/symmetric/previous
		ozra= point["oz_radius1"];		# oz radius
		ozr2= point["oz_radius2"];		# oz radius
		dist= point["distance"]/1000;		# distance in kms.
		if ozr2 <= 0:
			ozr2=500

		tpn=LT24tp[name[0:2]]
		tpname=tpn[0:6].strip()
		if   (wtyp == "start"):                 # convert from CU format to SW format
			type="Start"
			oz  ="Line"
			rad=ozra
			dist=0
			tp.append( tpname+".ss."+str(ozra)+" ")
			
		elif (wtyp == "finish"):
			type="Finish"
			oz  ="Cylinder"
			rad=ozra
			tp.append( tpname+".gl."+str(ozra)+" ")
		else:
			type="Turnpoint"
			oz  ="Cylinder"
			rad=ozr2
			tp.append( tpname+".gl.r"+str(ozr2)+" ")
		print "\t", "%-20s" % name, "\t\t", wtyp, type, oz, dist, ozty, ozra, ozr2, oz, type, rad, pidx        # print it as a reference
		ntp +=1					# number of TPs 
		tasklen += dist                         # compute the task distance
		
	print "=Task length: ", tasklen
	
	while ntp > 0:                                  # reverse the order of the TPs
                ntp -=1
                lt24wp += tp[ntp]
	TaskID=LT24date[taskdate][classtype] 		# get the task id and task password from the table
	Tpasswd='9611'
	lt24pre = "http://www.livetrack24.com/api.php?a=A43C46&cm=50;3;255;"+TaskID+";"+Tpasswd+";"+str(int(tasklen))+";"
	lt24buf = "t1.1 race wo1100 wc2300 so+0 tc2359 "+lt24wp
	lt24buf = lt24buf.strip()
	lt24str = lt24pre+lt24buf
	#print "LT24:", lt24str
	lt24url = lt24pre + urllib.quote_plus(lt24buf)
	#print "LT24:", lt24url
	#f=urllib2.urlopen(lt24url)

	if LT24login["error"] == "":
		print "LT24 op/ping", json.loads(lt24req("op/ping"))['ip']
		replygettask=lt24req("op/getTaskDef/taskID/"+TaskID)
		LT24gettask=json.loads(replygettask)
		print "LT24 TaskID="+TaskID, "was:", LT24gettask['taskDefinition']
		req = "op/setTask/taskID/"+TaskID+"/pass/"+Tpasswd+"/minDist/"+str(int(tasklen))+"/taskDef/"+urllib.quote_plus(lt24buf)
		replydeftask=lt24req(req)
		LT24deftask=json.loads(replydeftask)
		print "LT24 req="+req, LT24deftask['OK'] 
		if LT24deftask['OK'] != 1:
			print "LT24 op/getTaskDef/taskID/"+TaskID, lt24req("op/getTaskDef/taskID/"+TaskID)

	LT24pilot=json.loads(lt24req("op/getTaskPilots/taskID/"+TaskID))
	print LT24pilot['taskPilots'], "\n"
	LT24wp=json.loads(lt24req("/op/getCompWaypoints/taskID/"+TaskID))
	#print "LT24 Number of WP:", len(LT24wp['compWaypoints']), len(LT24tp.keys())
	if len(LT24wp['compWaypoints']) == len(LT24tp.keys()):
		continue
	else:
		exit(-1)
exit(0)
