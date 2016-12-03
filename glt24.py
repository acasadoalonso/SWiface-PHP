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
import lt24tasks

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

def getlt24tp(tp):
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
lt24tp={}
# ---------------------------------------------------------------- #
print "Util to get the api.soaringspot.com data and convert it to a LiveTrack24 API"
print "============================================================================\n\n"
print "Index day: ", idx, "Class requested: ", classreq, "\n\n"
print "Reading data from clientid/secretkey files"
# ===== SETUP parameters =======================#                                          
SWdbpath = config.DBpath                        # where to find the SQLITE3 database
initials = config.Initials			# initials of the files generated
cucpath="./cuc/"                                # where to store the JSON files
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
print date                                      #

local_time = datetime.datetime.now()            # the local time
print "Local Time is now:", local_time		# print the time for information only
fl_date_time = local_time.strftime("%Y%m%d")	# get the local time

getlt24tp   (lt24tp)
print "Total number of WayPoints on the LT24 file:" , len(lt24tp.keys())
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
ccc             =pycountry.countries.get(alpha2=country) # convert the 2 chars ID to the 3 chars ID
country3        =ccc.alpha3
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

		if   (wtyp == "start"):                 # convert from CU format to SW format
			type="Start"
			oz  ="Line"
			rad=ozra
			dist=0
			tpn=lt24tp[name[0:2]]
			tpname=tpn[0:3].strip()
			tp.append( tpname+".ss."+str(ozra)+" ")
			
		elif (wtyp == "finish"):
			type="Finish"
			oz  ="Cylinder"
			rad=ozra
			tpn=lt24tp[name[0:2]]
			tpname=tpn[0:3].strip()
			tp.append( tpname+".gl."+str(ozra)+" ")
		else:
			type="Turnpoint"
			oz  ="Cylinder"
			rad=ozr2
			tpn=lt24tp[name[0:2]]
			tpname=tpn[0:3].strip()
			tp.append( tpname+".gl.r"+str(ozr2)+" ")
		print "\t", "%-20s" % name, "\t\t", wtyp, type, oz, dist, ozty, ozra, ozr2, oz, type, rad, pidx        # print it as a reference
		ntp +=1					# number of TPs 
		tasklen += dist                         # compute the task distance
		
	print "=Task length: ", tasklen
	
	while ntp > 0:                                  # reverse the order of the TPs
                ntp -=1
                lt24wp += tp[ntp]
	TaskID=lt24tasks.lt24date[taskdate][classtype][0] # get the task id and task password from the table
	Tpasswd=lt24tasks.lt24date[taskdate][classtype][1]
	lt24pre = "http://www.livetrack24.com/api.php?a=A43C46&cm=50;3;255;"+TaskID+";"+Tpasswd+";"+str(int(tasklen))+";"
	lt24buf = "t1.1 race wo1100 wc2300 so+0 tc2359 "+lt24wp
	lt24buf = lt24buf.strip()
	lt24str = lt24pre+lt24buf
	#print "LT24:", lt24str
	lt24url = lt24pre + urllib.quote_plus(lt24buf)
	#print "LT24:", lt24url
	#f=urllib2.urlopen(lt24url)

	#LT24_appKey="A43C46"
	#LT24_appSecret="569024gn87894hdfg67dgd89dgmsm580165"


	f=open(LT24path+"clientid")                     # open the file with the client id
	client=f.read()                                 # read it
	LT24_appKey=client.rstrip()                     # clear the whitespace at the end
	f=open(LT24path+"secretkey")                    # open the file with the secret key
	secretkey=f.read()                              # read it
	LT24_appSecret=secretkey.rstrip()               # clear the whitespace at the end
	LT24qwe=" "
	print "op/ping", lt24req("op/ping")
	print "op/6/username/acasado/pass/xxxxxx", lt24req("op/6/username/acasado/pass/correo")
	print "op/ping", lt24req("op/ping")
	print "op/getTaskDef/taskID/"+TaskID, lt24req("op/getTaskDef/taskID/"+TaskID)
	req= "op/setTask/taskID/"+TaskID+"/pass/"+Tpasswd+"/minDist/"+str(int(tasklen))+"/taskDef/"+urllib.quote_plus(lt24buf)
	print req, lt24req(req)
	print "op/getTaskDef/taskID/"+TaskID, lt24req("op/getTaskDef/taskID/"+TaskID)
	print "op/getTaskPilots/taskID/"+TaskID, lt24req("op/getTaskPilots/taskID/"+TaskID)
	print "op/getTaskPilotsDetailed/taskID/"+TaskID, lt24req("op/getTaskPilotsDetailed/taskID/"+TaskID)
exit(0)
