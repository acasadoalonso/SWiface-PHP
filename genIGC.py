import sys
from datetime import *
from geofuncs import *
########################################################################
def gdatar (data, typer):               	# get data on the  right
        p=data.find(typer)              	# scan for the type requested
        if p == -1:
                return (" ")
        p=p+len(typer)
        pb=p+1
        max=len(data)-1
        while (pb < max):
                if data[pb] == ' ' or data[pb] == '\n' or data[pb] == '\r' :
                        break
                pb += 1
        ret=data[p:pb]                  	# return the data requested
        return(ret)
########################################################################

#
# this program reads from standard input the results of the grep & sort the IGC files with the FLARM data and try to build an IGC file
#
date=datetime.now()                         # get the date
dte=date.strftime("%y%m%d")                 # today's date

print 'AGNE001GLIDER'                       # write the IGC header
print 'HFDTE'+dte                           # write the date on the header

for line in sys.stdin:                      # read one line
    p1=line.find(">>>")
    pos=line[p1+4:p1+36+4]                  # get the original position
    ttime=pos[1:7]                          # the time
    lat=pos[7:15]                           # latitude
    lon=pos[15:24]                          # longitude
    palt=pos[25:30]                         # pressuere altitude
    galt=pos[30:35]                         # GPS altitude
    north=gdatar(line, "North:")
    east=gdatar(line,"East:")
    down=gdatar(line, "Down:")
    N=int(north)
    E=int(east)
    D=int(down)
    pa=int(palt)-D
    ga=int(galt)-D
    ppa="A%05d"%pa
    gga="%05d"%ga
    #print ttime, lat, lon, palt, galt, N, E, D, pos, line
    npos=getnewDMS(lat, lon, ga, N, E, D)
    print "B"+ttime+npos[0]+npos[1]+ppa+gga
    print "LIGC >>"+line.rstrip('\n\r')
