import datetime
import time
import sys
since  =sys.argv[1]
datetimes=datetime.datetime.utcfromtimestamp(int(since))
date=     datetimes.strftime("%y%m%d")
time=     datetimes.strftime("%H%M%S")
print date, time
