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
import math
import os
import socket
import config

from simplehal import HalDocument, Resolver
from pprint import pprint

#-------------------------------------------------------------------------------------------------------------------#

from config import fixcoding

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
	print "TTT", classreq
else:
        classreq=' '                            # none        
# ---------------------------------------------------------------- #
print "\n\n"
print "Utility to get the api.soaringspot.com data and extract all the PILOT information needed for FlyTool  V1.0"
print "==========================================================================================================\n\n"
print "Index day: ", idx, " Class requested: ", classreq
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
hostname=socket.gethostname()			# hostname as control
print "Hostname:", hostname
start_time = time.time()                        # get the time now
utc = datetime.datetime.utcnow()                # the UTC time
print "UTC Time is now:", utc  	                # print the time for information only
date = utc.strftime("%Y-%m-%dT%H:%M:%SZ")       # get the local time
print date                                      #

local_time = datetime.datetime.now()            # the local time
print "Local Time is now:", local_time		# print the time for information only
fl_date_time = local_time.strftime("%Y%m%d")	# get the local time
print "Config params.  SECpath:", secpath

#nonce=base64.b64encode(OpenSSL.rand.bytes(36))  # get the once base
nonce=base64.b64encode(os.urandom(36))          # get the once base
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

category        =cd['category']                 # get the main data from the contest 
eventname       =cd['name']
compid          =cd['id']
country         =cd['country']                  # country code - 2 chars code
compcountry     =country				# contry as defaults for pilots
ccc             =pycountry.countries.get(alpha_2=country) # convert the 2 chars ID to the 3 chars ID
country         =ccc.alpha_3
endate          =cd['end_date']
lc              =getemb(cd,'location')          # location data 
lcname          =lc['name']                     # location name

print "\n\n= Contest ==============================="
print "Category:", category,"Comp name:", eventname, "Comp ID:", compid
print "Loc Name:", lcname,   "Country: ", country, country, "End date:",  endate
print "=========================================\n\n"

npil=0                                          # init the number of pilots
nwarnings=0                                     # number of warnings ...
warnings=[]                                     # warnings glider
classes=[]
pilots=[]
# Build the tracks and turn points, exploring the contestants and task within each class
                                                # go thru the different classes now within the daya

print "Classes:\n========\n\n"

for cl in getemb(cd,'classes'):
        #print "CLCLCL", cl
        classname= cl["type"]                   # search for each class
        print "Class:", classname,"\n\n"        # search for each class
        url3=getlinks(cl, "contestants")        # search for the contestants on each class
        ctt=gdata(url3,   "contestants")        # get the contestants data
        #print "CTTCTT",ctt
        pilots=[]
        for contestants in ctt:
                #print "FT", ft, "\n\n"
                fname=getemb(contestants,'pilot')[0]['first_name']
                lname=getemb(contestants,'pilot')[0]['last_name']
                pname=fixcoding(fname+" "+lname).encode('utf-8').decode('utf-8')  # convert it to utf8 in order to avoid problems
                if 'club' in contestants:
                        club=fixcoding(contestants['club']).encode('utf-8').decode('utf-8')
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

                if 'nationality' in getemb(contestants,'pilot')[0]:
                        nation     =getemb(contestants,'pilot')[0]['nationality']
                else:

                        if compcountry != '':
                                nation=compcountry
                        else:
                                nation="ES"             # by default is SPAIN
                ccc             =pycountry.countries.get(alpha_2=nation) # convert the 2 chars ID to the 3 chars ID
                country3        =ccc.alpha_3
                if 'email'       in getemb(contestants,'pilot')[0]:
                        email      =getemb(contestants,'pilot')[0]['email']
                else:
                        email="email_NOTYET"
                igcid=getemb(contestants,'pilot')[0]['igc_id']

                print "Pilot:",  pname, "Club:", club, "CompID:", cn, "Nation:", nation, "Country Code", country3, "Email:", email, "IGCID:", igcid
                npil += 1
                pil={"PilotName": pname, "Club": club, "CompID":  cn, "Nation":  nation, "CountryCode": country3, "Email":  email, "IgcID":  igcid, "PortraitUrl": "http://rankingdata.fai.org/PilotImages/"+str(igcid)+".jpg"} 
                pilots.append(pil)
        cll={"Class":classname, "Pilots": pilots}
        classes.append(cll)
        print "----------------------------------------------------------------\n\n"



print "= Pilots ===========================", npil, "\n\n"      # print the number of pilots as a reference and control
FlyTool={"Compname": eventname, "Category": category, "Country": country, "EndDate": endate, "Location": lcname, "Classes": classes}

jsonfile=open("FlyTool.json", 'w')
j=json.dumps(FlyTool, indent=4)
jsonfile.write(j)
jsonfile.close()
print j


