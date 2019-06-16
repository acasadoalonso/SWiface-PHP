from geofuncs import *
p1=geopy.Point(50.62275, 22.00905, 283)
lat=50.62275
lon=22.00905
alt=283
N=637
E=-1100
D=142
pp=getnewpos(lat, lon, alt, N, E, D)
print pp.latitude, pp.longitude
l="5037173N"
lo="02201094E"
alt=00410
N=935
E=-1646
D=273
lat=DDMMmmm2lat(l)
lon=DDMMmmm2lon(lo)
print lat, lon
pp=getnewpos(lat, lon, alt, N, E, D)
print pp.latitude, pp.longitude

            
