from datetime 	import datetime
from pytz 	import timezone
 
dt=datetime(1970,1,1)
cet=timezone("CET")
lt=cet.localize(dt)
offset=lt.utcoffset()
print offset.total_seconds()
