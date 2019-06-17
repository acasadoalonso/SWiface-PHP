from geofuncs import *
from   geopy.distance import vincenty

nla=50.62794925
nlo=21.9949283

l= "5037197N"
lo="02201019E"
alt=00410
N=935
E=-1646
D=273
lat=DDMMmmm2lat(l)
lon=DDMMmmm2lon(lo)
print "From:", l,lo,"-->", lat, lon
pp=getnewpos(lat, lon, alt, N, E, D)
print "To:  ",pp.latitude, pp.longitude
dist=vincenty((nla, nlo), (pp.latitude,pp.longitude)).km
print "Dist:",dist
print nla, "==>", decdeg2DDMMmmm(nla)
print nlo, "==>", decdeg2DDMMmmm(nlo)
print nla, "==>", tolatDDMMmmm(nla)
print nlo, "==>", tolonDDMMmmm(nlo)

print l, lo, "==> New:  ",getnewDDMMmmm(l, lo, alt, N, E, D), "\n\n"

nla=DDMMmmm2lat(l)
print l, "==>", nla , "==>", decdeg2DDMMmmm(nla), tolatDDMMmmm(nla)
nlo=DDMMmmm2lon(lo)
print lo, "==>", nlo, "==>", decdeg2DDMMmmm(nlo), tolonDDMMmmm(nlo)
n=40.123456
lll= decdeg2DDMMmmm(nla)
print nla , "-->", lll, tolatDDMMmmm(n), DDMMmmm2decdeg(lll[0], lll[1], lll[2])
lll= decdeg2DDMMmmm(nlo)
print nlo , "-->", lll, tolonDDMMmmm(n), DDMMmmm2decdeg(lll[0], lll[1], lll[2])

