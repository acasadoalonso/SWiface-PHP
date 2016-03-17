import sqlite3
import os
filename="cucfiles/contest.db"
fd = os.open(filename, os.O_RDONLY)
conn = sqlite3.connect('/dev/fd/%d' % fd)
cursD=conn.cursor()                                             # cursor for the CONTESTANT table
cursD.execute ('select * from PILOT')
for row in cursD.fetchall():
    print row
    eventname=row[2]

os.close(fd)
