from datetime 	import datetime
from pytz 	import timezone
import os
cuc=os.listdir('cuc')
for fn in cuc:
	ft=fn[fn.find('.')+1:]
	if (ft == 'cuc'):
		LQ=fn[0:4]
		print fn, LQ, ft
		y=int(fn[4:8])
		m=int(fn[8:10])
		d=int(fn[10:12])
 		td=datetime(y,m,d)-datetime(1970,1,1)
		ts=td.total_seconds()
		print fn, ts
