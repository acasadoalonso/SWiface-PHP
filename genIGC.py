#!/usr/bin/python3
#
# This script get all files with the FLARM messages and rebuild the files with the information of the FLARM embeded on the other IGC files
#

import sys
from datetime import *
from geofuncs import *
from ogndata import *
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
date = datetime.now()                   # get the date
dte = date.strftime("%y%m%d")           # today's date
flarmID = str(sys.argv[1:])[2:8]        # see the FlarmID requested


print('AGNE001GLIDER')                  # write the IGC header
print('HFDTE'+dte)                      # write the date on the headera
print("HFPLTPILOTINCHARGE:"+flarmID)    # Flarm ID
print("HFDTM100GPSDATUM:WGS-1984")      # Datum
print("HFGIDGLIDERID:"+getognreg(flarmID))   # registration ID
print("HFCIDCOMPETITIONID:"+getogncn(flarmID))  # competition ID
print("HFFTYFRTYPE:FLrebuild")          # Flarm rebuild

for line in sys.stdin:                  # read one line
    p1 = line.find(">>>")
    if p1 == -1:                        # this should never happens
        continue                        # ignore this record
    pos = line[p1+4:p1+36+4]            # get the original position
    ttime = pos[1:7]                    # the time
    lat = pos[7:15]                     # latitude
    lon = pos[15:24]                    # longitude
    palt = pos[25:30]                   # pressuere altitude
    galt = pos[30:35]                   # GPS altitude
    north = gdatar(line, "North:")      # get the N data
    east =  gdatar(line, "East:")       # get the E data
    down =  gdatar(line, "Down:")       # get the D data
    try:
        N = int(north)
        E = int(east)
        D = int(down)
        pa = int(palt)-D                # the new pressure altitude
        ga = int(galt)-D                # get the GPS altitude
    except:
        print(">:>LINE:", line)
    ppa = "A%05d" % pa                  # format the pressure altitude
    gga = "%05d" % ga                   # format the GPS altitude
    #print ttime, lat, lon, palt, galt, N, E, D, pos, line
                                        # get the new coordinates based on the vector NED
    npos = getnewDDMMmmm(lat, lon, ga, N, E, D)
    print("B"+ttime+npos[0]+npos[1]+ppa+gga)    # set the new IGC record
    print("LIGC >>"+line.rstrip('\n\r'))        # write the L record as control
