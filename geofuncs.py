# Geo routines
import math
import geopy
import geopy.distance
##########################################################################
def decdeg2dms(dd):              # convert degrees to D, M, S
    
    negative = dd < 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600,60)
    degrees,minutes = divmod(minutes,60)
    if negative:
        if degrees > 0:
            degrees = -degrees
        elif minutes > 0:
            minutes = -minutes
        else:
            seconds = -seconds
    return (degrees,minutes,seconds)

def decdeg2DDMMmmm(dd):         # convert degrees to D, M, DM
    
    negative = dd < 0
    dd = abs(dd)
    
    """decimal degrees to deg dec min"""
    deg = int(dd)
    minsec = (dd - deg)*60.0
    
    minutes=float(int(minsec))
    
    mindec=(minsec-minutes)*1000.0
    
    if negative:
        if deg > 0:
            deg = -deg
    return (float(deg),minutes,mindec)

def dms2decdeg(g, m, s):        # convert DDMMSS to degrees
    
    return (float(g)+float(m)/60.0+float(s)/3600.0)

def DDMMmmm2decdeg(g, m, dm):   # convert DDMMmmm to degrees
    
    return (float(g)+(float(m)+float(dm)/1000.0)/60.0)

def tolatDMS(dd):               # convert degrees to string DDMMSS
    
        x=decdeg2dms(dd)
        if dd > 0:
            fmt="%02d%02d%02d0N"
        else:
            fmt="%02d%02d%02d0S"
        return (fmt%x)
    
def tolatDDMMmmm(dd):           # convert degrees to string DDMMmmm
    
        x=decdeg2DDMMmmm(dd)
        if dd > 0:
            fmt="%02d%02d%03dN"
        else:
            fmt="%02d%02d%03dS"
        return (fmt%x)
    
def tolonDMS(dd):               # convert degrees to string DDDMMSS
    
        x=decdeg2dms(dd)
        if dd > 0:
            fmt="%03d%02d%02d0E"
        else:
            fmt="%03d%02d%02d0W"
        return (fmt%x)

def tolonDDMMmmm(dd):           # convert degrees to DDDMMmmm 
    
        x=decdeg2DDMMmmm(dd)
        if dd > 0:
            fmt="%03d%02d%03dE"
        else:
            fmt="%03d%02d%03dW"
        return (fmt%x)

def DMS2lat(lat):               # convert string DDMMSS to degrees
    
        l=dms2decdeg(int(lat[0:2]), int(lat[2:4]), int(lat[4:6]))
        if lat[6:7] == 'N':
            return l
        if lat[6:7] == 'S':
            return -l
        else:
            return 0
            
def DDMMmmm2lat(lat):           # convert string DDMMmmm to degrees
        l=DDMMmmm2decdeg(int(lat[0:2]), int(lat[2:4]), int(lat[4:7]))
        
        if lat[7:8] == 'N':
            return l
        if lat[7:8] == 'S':
            return -l
        else:
            return 0 

def DMS2lon(lon):               # convert string DDDMMSS to degrees
    
        l=dms2decdeg(int(lon[0:3]), int(lon[3:5]), int(lon[5:7]))
        if lon[7:8] == 'E':
            return l
        if lon[7:8] == 'W':
            return -l
        else:
            return 0
def DDMMmmm2lon(lon):           # convert string DDDMMmmm to degrees
    
        l=DDMMmmm2decdeg(int(lon[0:3]), int(lon[3:5]), int(lon[5:8]))
        if lon[8:9] == 'E':
            return l
        if lon[8:9] == 'W':
            return -l
        else:
            return 0

##########################################################################
# add the NED North, East, Down to a current position
def getnewpos(lat, lon, alt, N, E, D):
# Define starting point.
    start = geopy.Point(lat, lon, alt)

# Define a general distance object, initialized with a distance of 1 km.
    dN = geopy.distance.VincentyDistance(kilometers = N/1000.0) # get the distance as a point
    dE = geopy.distance.VincentyDistance(kilometers = E/1000.0)

# Use the `destination` method with a bearing of 0 degrees (which is north)
# in order to go from point `start` 1 km to north.
    d1=dN.destination(point=start, bearing=0)           # go North
    d2=dE.destination(point=d1, bearing=90)             # go Easta
    #print "\n", d1, "\n", d2
    return (d2)                                         # return the result

def getnewcoor(lat, lon, alt, N, E, D):                 # get new coordenates DMS adding NED
    p=getnewpos(lat, lon, alt, N, E, D)                 # get the new position
    lat=tolatDDMMmmm(p.latitude)                        # the new latitude DMS
    lon=tolonDDMMmmm(p.longitude)                       # the new longitude DMS 
    return (lat, lon, alt-D)

def getnewDDMMmmm(lat, lon, alt, N, E, D):              # get the new DMS from DMS adding NED
    lt=DDMMmmm2lat(lat)                                 # convert to decimal degree
    ln=DDMMmmm2lon(lon)                                 #
    return(getnewcoor(lt, ln, alt, N, E, D))            # return the tuple in DMS format as well

##########################################################################
