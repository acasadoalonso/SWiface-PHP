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
import socket
import config
from  ogndata   import *
from  getflarm  import *
from  simplehal import HalDocument, Resolver
from  pprint    import pprint
from  config    import *

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
###################################################################
day         =sys.argv[1:]                       # see if index day is requestedd        
clsreq      =sys.argv[2:]                       # if class is requested
execreq     =sys.argv[3:]                       # -e request
FlarmIDr    =sys.argv[4:]                       # -e request the FlarmID
if day and day[0].isdigit():                    # if provided and numeric
        idx=int(day[0])                         # index day 
else:
        idx=0
if clsreq:
        classreq=clsreq[0]                      # class requested
        print "Class requested:", classreq
        if classreq == "ALL":
            classreq=' ' 
else:
        classreq=' '                            # none     
FlarmID=""                                      # the FlarmID of the files to be reconstructed
execopt=False
if execreq and execreq[0]=="-e":                # if we ask to exec the buildIGC
    if FlarmIDr:
        FlarmID=FlarmIDr[0]                     # get the FlarmID
        execopt=True

# ---------------------------------------------------------------- #
print "Utility to get the api.soaringspot.com data and extract all the IGC files from the SoaringSpot server V1.1"
print "==========================================================================================================\n\n"
print "Usage:   python soa2fil.py indexday class [-e FlarmID ]"
print "=======================================================\n\n"
print "Index day: ", idx, " Class requested: ", classreq, FlarmID
print "Reading data from clientid/secretkey files"
print "==========================================\n\n"
# ===== SETUP parameters =======================#                                          
SARpath = config.SARpath                        # where to get/store the IGC files
cwd=os.getcwd()					# get the current working directory
secpath=cwd+"/SoaringSpot/"                     # where to find the clientid and secretkey files 
apiurl="http://api.soaringspot.com/"            # soaringspot API URL
rel="v1"                                        # we use API version 1
taskType= "SailplaneRacing"                     # race type
dirpath=SARpath+"/IGCfiles/"                    # the subdirectory where to store the extracted files
if execopt:                                     # if we choose the option of gen the IGC file
    
    os.system ("rm "+dirpath+"*/*")             # delete all the files to avoid problems

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

category        =cd['category']
eventname       =cd['name']
compid          =cd['id']
country         =cd['country']                  # country code - 2 chars code
compcountry     =country				# contry as defaults for pilots
ccc             =pycountry.countries.get(alpha_2=country) # convert the 2 chars ID to the 3 chars ID
country3        =ccc.alpha_3
endate          =cd['end_date']
lc              =getemb(cd,'location')          # location data 
lcname          =lc['name']                     # location name

print "\n\n= Contest ==============================="
print "Category:", category,"Comp name:", eventname, "Comp ID:", compid
print "Loc Name:", lcname,   "Country: ", country, country3, "End date:",  endate
print "=========================================\n\n"

npil=0                                          # init the number of pilots
stats={}                                        # statistics 
prt=False                                       # print ???
igcdir=''                                       # directory where it goes the IGC files

# Build the tracks and turn points, exploring the contestants and task within each class
                                                # go thru the different classes now within the daya
PrevTaskDate=""
print "Classes:\n========\n\n"

for cl in getemb(cd,'classes'):
        #print "CLCLCL", cl
        classname= cl["type"]                   # search for each class
        print "Class:", classname,"\n\n"        # search for each class
	url3=getlinks(cl, "class_results")      # search for the contestants on each class
        if  len(gdata(url3,   "class_results", prt='no')) > idx :
	    ctt=gdata(url3,   "class_results", prt='no') [idx]       # get the results data
        else:
            print "The class ", classname, "it is not ready yet\n"
            continue                            # the class is not ready
        #print "CTTCTT",ctt
        tasktype=ctt["task_type"]
        taskdate=ctt["task_date"]
        print "Task Type: ", tasktype, "Task date: ", taskdate
        if PrevTaskDate == "":                  # check the cases where the task dates are not the same within an index day
             PrevTaskDate =  taskdate
        elif PrevTaskDate != taskdate:
            print ">>>>Warning: Task dates are different for the same index day !!!"
        fft=getemb(ctt, "results")              # go to the results data
        for ft in fft:
                #print "FT", ft, "\n\n"
                cnt=getemb(ft, "contestant")    # go the contestants (pilot) information 
                pil=getemb(cnt, "pilot")[0]     # get the pilot name information 
                npil += 1
                if "igc_file" in ft:
                    fftc=getlinks(ft, "flight") # URL to the file to be downloaded 
                    igcfile=ft["igc_file"]      # full IGC file DIR/IGCfilename
                    igcdir=igcfile[0:3]         # the first 3 char are the directory where it goes for example: 95I 
                else:
                    print ">>> missing FILE >>>>>", fixcoding(pil["first_name"]).encode('utf8'), fixcoding(pil["last_name"])
                    continue
                igcfilename=dirpath+"/"+igcfile[0:3]+"/"+classname+"-"+igcfile[4:]
                if not os.path.isdir(dirpath+"/"+igcfile[0:3]):
                    os.system("mkdir "+dirpath+"/"+igcfile[0:3])
                    print " OK directory made"  # create the directory if needed 
                if "nationality" in pil:        # extracts the nationality as a doc
                    nationality=pil['nationality']
                else:
                    nationality="UNKOWN"        # report that we are extracting the flight of that pilot
                print "Pilot:>>>>", fixcoding(pil["first_name"]).encode('utf8'), fixcoding(pil["last_name"]), nationality
      	        req = urllib2.Request(fftc)     # open the URL                      
                req.add_header('Authorization', auth)   # build the authorization header
                req.add_header("Accept","application/json")
                req.add_header("Content-Type","application/hal+json")
                r = urllib2.urlopen(req)        # open the url resource
                #fff=r.read()
                # call the routine that will read the file and handle the FLARM records
                cnt=getflarmfile(r, igcfile, igcfilename, stats, prt)
                if prt:
                    print "Number of records:", igcfilename, cnt
                print "----------------------------------------------------------------"
        print "----------------------------------------------------------------\n\n"
print stats
#
# Check if the exec option is requested
#
if execopt:
    cwd=os.getcwd()
    print "Extracting the IGC file from embeded FLARM messages \nFrom CD:", cwd, "To:", dirpath
    if os.path.isdir(dirpath):
        os.chdir(dirpath)                               # report current directory and the new one
    else:
        print "Not available target directory:", dirpath+igcdir

    fname=FlarmID+'.'+getognreg(FlarmID)+'.'+getogncn(FlarmID)+'.igc'
    if os.path.isfile(fname):                           # remove the file to avoid errors
        os.remove(fname)                                # remove if exists
                                                        # get the new IGC files based on the FLARM messages
    os.system('grep "FLARM "'+FlarmID+' */* | sort -k 3 | python '+cwd+'/genIGC.py '+FlarmID+' > '+fname)
    print "Resulting IGC file is on:", dirpath, "As: ", fname


print "= Pilots ===========================", npil      # print the number of pilots as a reference and control



