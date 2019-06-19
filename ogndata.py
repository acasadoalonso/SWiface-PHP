import json
import urllib2
global ogninfo                                  # the OGN info data
ogninfo={}                                      # the OGN info data
####################################################################
def getogndata():                               # get the data from the API server

        url="http://ddb.glidernet.org/download/?j=1"
	req = urllib2.Request(url)                      
	req.add_header("Accept","application/json")
	req.add_header("Content-Type","application/hal+json")
	r = urllib2.urlopen(req)                # open the url resource
	j_obj = json.load(r)                    # convert to JSONa
        ogninfo=j_obj                           # save the data
	return j_obj                            # return the JSON object

def getognreg(flarmid ):                        # get the ogn registrafrion from the flarmID

        global ogninfo                          # the OGN info data
        if len(ogninfo) == 0:
            ogninfo=getogndata()
        devices=ogninfo["devices"]              # access to the ogndata
        for dev in devices:                     # loop into the registrations
            if dev["device_id"] == flarmid:     # if matches ??
                return dev["registration"]      # return the registration

        return "NOREG  "                        #if not found !!!

def getognflarmid(registration ):               # get the ogn flarmID from the registration

        global ogninfo                          # the OGN info data
        if len(ogninfo) == 0:
            ogninfo=getogndata()
        devices=ogninfo["devices"]              # access to the ogndata
        for dev in devices:                     # loop into the registrations
            if dev["registration"] == registration: # if matches ??
                if   dev['device_type'] == "F":
                     dvce="FLR"+dev['device_id'] 
                elif dev['device_type'] == "I":
                     dvce="ICA"+dev['device_id'] 
                elif dev['device_type'] == "O":
                     dvce="OGN"+dev['device_id'] 
                else:
                     dvce="UNK"+dev['device_id'] 

                return dvce                     # return the flarmID

        return "NOREG  "                        #if not found !!!

def getogncn(flarmid ):                         # get the ogn registrafrion from the flarmID

        global ogninfo                          # the OGN info data
        if len(ogninfo) == 0:
            ogninfo=getogndata()
        devices=ogninfo["devices"]              # access to the ogndata
        for dev in devices:                     # loop into the registrations
            if dev["device_id"] == flarmid:     # if matches ??
                return dev["cn"]                # return the registration

        return "NOC"                            # if not found !!!

###################################################################

