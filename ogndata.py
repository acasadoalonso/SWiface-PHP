import json
import urllib2

####################################################################
def getogndata():                               # get the data from the API server

        url="http://ddb.glidernet.org/download/?j=1"
	req = urllib2.Request(url)                      
	req.add_header("Accept","application/json")
	req.add_header("Content-Type","application/hal+json")
	r = urllib2.urlopen(req)                # open the url resource
	j_obj = json.load(r)                    # convert to JSON
	return j_obj                            # return the JSON object

def getognreg(flarmid, ogninfo):                # get the ogn registrafrion from the flarmID
        devices=ogninfo["devices"]              # access to the ogndata
        for dev in devices:                     # loop into the registrations
            if dev["device_id"] == flarmid:     # if matches ??
                return dev["registration"]      # return the registration

        return "NOREG  "                        #if not found !!!

def getogncn(flarmid, ogninfo):                 # get the ogn registrafrion from the flarmID
        devices=ogninfo["devices"]              # access to the ogndata
        for dev in devices:                     # loop into the registrations
            if dev["device_id"] == flarmid:     # if matches ??
                return dev["cn"]                # return the registration

        return "NOC"                            # if not found !!!

###################################################################

