import json
import urllib2
qsgpID=14
numberofdays=9
j = urllib2.urlopen('http://www.crosscountry.aero/c/sgp/rest/comp/'+str(qsgpID))
j_obj = json.load(j)
#print j_obj
j=json.dumps(j_obj, indent=4)
#
# the different pieces of information
#
pilots=j_obj["p"]
print "Pilots"
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
print "Competition"
comp=j_obj["c"]
comp_firstday=comp['a']
comp_lastday=comp['b']
comp_name=comp['t']
comp_shortname=comp['l']
comp_id=comp['i']
print comp_id, comp_name, comp_shortname, comp_firstday, comp_lastday
print "Index of Days"
numberofactivedays=j_obj["j"]
indexofdays=j_obj["i"]
#print indexofdays
print "Number of days: ", numberofdays
day=0
daysids=[]
while day < numberofdays:
	date= indexofdays[day]["d"]    
	title= indexofdays[day]["t"]    
	shorttitle= indexofdays[day]["l"]    
	starttime= indexofdays[day]["a"]    
	daytype= indexofdays[day]["y"]    
	dayid= indexofdays[day]["i"]  
	daysids.append(dayid)
	print date, title, shorttitle, starttime, daytype, dayid
	day +=1
print daysids
day=0
while day < numberofdays:
	d = urllib2.urlopen('http://www.crosscountry.aero/c/sgp/rest/day/'+str(qsgpID)+'/'+str(daysids[day]))
	d_obj = json.load(d)
	d=json.dumps(d_obj, indent=4)

	print "Day: ", day, "DayID: ", daysids[day]
	#print d
	comp_day=d_obj["@type"]
	comp_id=d_obj["e"]
	comp_dayid=d_obj["i"]
	comp_date=d_obj["d"]
	comp_daytype=d_obj["y"]
	comp_shortdaytitle=d_obj["t"]
	comp_starttime=d_obj["a"]
	comp_startaltitude=d_obj["h"]
	comp_finishaltitude=d_obj["f"]
	comp_taskinfo=d_obj["k"]
	print comp_day, comp_id, comp_dayid, comp_shortdaytitle, comp_starttime, comp_startaltitude, comp_finishaltitude
	day +=1
	task_type=comp_taskinfo["@type"]
	task_id=comp_taskinfo["id"]
	task_listid=comp_taskinfo["taskListId"]
	task_name=comp_taskinfo["name"]
	task_data=comp_taskinfo["data"]
	
	task_at=task_data["at"]	
	task_wp=task_data["g"]	
	task_wpla=task_data["u"]
	task_wptlist=task_wpla["wptList"]	
	print task_type, task_id, task_listid, task_name, task_at, task_wptlist
	#print "WP:==>", task_wp
	wp=0
	while wp < task_wptlist:
		#print "WP#:", wp
		wp_name=task_wp[wp]["n"]
		if wp == 0:
			wpinit=wp_name
		wp_lat=task_wp[wp]["a"]
		wp_lon=task_wp[wp]["o"]
		wp_type=task_wp[wp]["y"]
		wp_radius=task_wp[wp]["r"]
		#wp_idCode=task_wp[wp]["idCode"]
		print wp_name, wp_lat, wp_lon,  wp_type, wp_radius
		if wp > 0 and  (wp_name == wpinit or wp_type=="line"):
			break
		wp +=1

	print "WP:================================>"
