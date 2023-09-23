#!/usr/bin/python3
#
# This script get all files with the FLARM messages and rebuild the files with the information of the FLARM embeded on the other IGC files
#

import sys
from datetime import *
from geofuncs import *
from ognddbfuncs import *
from geopy.distance import geodesic
from parserfuncs import getinfoairport
from pytz import timezone
import config
########################################################################


def gdatar(data, typer):                # get data on the  right
    p = data.find(typer)                # scan for the type requested
    if p == -1:                         # if not found
        return (" ")
    p = p+len(typer)
    pb = p+1
    max = len(data)-1
    while (pb < max):
        if data[pb] == ' ' or data[pb] == '\n' or data[pb] == '\r':
            break
        pb += 1
    ret = data[p:pb]                 	# return the data requested
    return(ret)
########################################################################


#
# this program reads from standard input the results of the grep & sort the IGC files with the FLARM data and try to build an IGC file
#

# -----------------------------------------------------------------------------------

if getinfoairport (config.locname) != None:
   #print(getinfoairport (config.locname), file=sys.stderr)
   loclatitude = getinfoairport (config.locname)['lat']
   loclongitud = getinfoairport (config.locname)['lon']
   timezn      = getinfoairport (config.locname)['tz']
   tz = timezone(timezn)
   
else:
   loclatitude = config.loclatitude
   loclongitud = config.loclongitud
print("Location coordinates:", loclatitude, loclongitud, "at: ", config.locname, timezn, file=sys.stderr)

date = datetime.now()                   # get the date
offset=tz.utcoffset(date).seconds/3600.0 # TZ offset
dte = date.strftime("%y%m%d")           # today's date
flarmID = str(sys.argv[1:])[2:8]        # see the FlarmID requested
lastloclat=0.0
lastloclon=0.0
lastalt=0

print('AGNE001GLIDER')                  # write the IGC header
print('HFDTE'+dte)                      # write the date on the headera
print('HFFXA015') 
print("HFPLTPILOTINCHARGE:"+flarmID)    # Flarm ID
print("HFDTM100GPSDATUM:WGS-1984")      # Datum
print("HFGIDGLIDERID:"+getognreg(flarmID))   # registration ID
print("HFCIDCOMPETITIONID:"+getogncn(flarmID))  # competition ID
print("HFFTYFRTYPE:FLrebuild")          # Flarm rebuild
print("HFTZNTIMEZONE:"+str(offset))
nline=0
nerr=0
nrec=0
distance=0.0
disthome=0.0
lastdist=0.0
diffalt=0
for line in sys.stdin:                  # read one line
    nline += 1
    p1 = line.find(">>>")
    if p1 == -1:                        # this should never happens
        continue                        # ignore this record
    pos   = line[p1+4:p1+36+4]          # get the original position
    ttime = pos[1:7]                    # the time
    lat   = pos[7:15]                   # latitude
    lon   = pos[15:24]                  # longitude
    palt  = pos[25:30]                  # pressuere altitude
    galt  = pos[30:35]                  # GPS altitude
    north = gdatar(line, "North:")      # get the N data
    east  = gdatar(line, "East:")       # get the E data
    down  = gdatar(line, "Down:")       # get the D data
    try:
        N  = int(north)
        E  = int(east)
        D  = int(down)
        pa = int(palt)-D                # the new pressure altitude
        ga = int(galt)-D                # get the GPS altitude
    except:
        print(">:>Invalid LINE:", nline, line, file=sys.stderr)
        print(ttime, lat, lon, palt, galt,  pos, file=sys.stderr)
        continue
    loclat=float(lat[0:6])/10000.0
    if lat[7] == 'S':
       loclat *= -1.0
    loclon=float(lon[0:7])/10000.0
    if lon[8] == 'W':
       loclon *= -1.0
    if nline != 1:
       distance=geodesic((loclat, loclon), (lastloclat,lastloclon)).km		# distance to previus position
       disthome=geodesic((loclat, loclon), (loclatitude,loclongitud)).km	# distance to HOME
       diffalt=pa-lastalt
    else:				# line first
       lastloclat=loclat		# INITIAL LOCATION
       lastloclon=loclon
       lastalt=pa
       
    #print("DDD", nline, lat, lon,loclat,loclon, "D: ", distance, lastloclat, lastloclon)
    if disthome < 80.0 and abs(diffalt) < 500:
       lastloclat=loclat		# remeber last location
       lastloclon=loclon
       lastdist=distance
       lastalt=pa			# remember altitude
    else:
       pass
       lastalt=pa			# remember altitude
       nerr += 1
       print("DDD", nline, nerr, "D: ", distance, disthome, diffalt, lastdist, lat,loclon, lastloclat, lastloclon,  file=sys.stderr)
       continue
    ppa = "A%05d" % pa                  # format the pressure altitude
    gga = "%05d" % ga                   # format the GPS altitude
    #print ttime, lat, lon, palt, galt, N, E, D, pos, line
                                        # get the new coordinates based on the vector NED
    npos = getnewDDMMmmm(lat, lon, ga, N, E, D)
    print("B"+ttime+npos[0]+npos[1]+ppa+gga)    # set the new IGC record
    print("LIGC ", nline, distance, disthome, ">>>"+line.rstrip('\n\r'))        # write the L record as control
    nrec += 1
print ("File processed: Input lines ", nline, " Errors: ", nerr, " Total output lines: ", nrec, file=sys.stderr) 
