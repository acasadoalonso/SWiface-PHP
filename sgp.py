import json
import urllib2
j = urllib2.urlopen('http://www.crosscountry.aero/c/sgp/rest/comp/14')
j_obj = json.load(j)
#print j_obj
j=json.dumps(j_obj, indent=4)
#print j
day=j_obj["d"]
j=json.dumps(day, indent=4)
print j
pilots=j_obj["p"]
#print pilots
for id in pilots:
	#print id
	#print pilots[id]
#                        
	pid= pilots[id]["i"]    
	k= pilots[id]["k"]    
	e= pilots[id]["e"]    
	fname= pilots[id]["f"]    
	lname= pilots[id]["l"]    
	compid= pilots[id]["d"]    
	country= pilots[id]["z"]    
	model= pilots[id]["s"]    
	j= pilots[id]["j"]    
	rankingid= pilots[id]["r"]
	print pid, k, e, fname, lname, compid, country, model, j, rankingid    
