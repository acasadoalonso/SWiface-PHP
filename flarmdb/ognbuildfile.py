#!/usr/bin/env python
#
# Program to read OGN  database and create a file as the base for known gliders
#
import sys
sys.path.insert(0, '/var/www/html')
import config

import string
import requests
import time
import sqlite3

def ogndb (prt, curs):
    
    
    db      = open("ognddbdata.csv", 'r')
    flm_txt = open("ognddbdata.txt",'w')
    
    print "Process OGN databse"
    line = db.readline()
    if prt:
        print "Format: ", line
    i = 1
    line = ""
     
    while True:
        try:
            line = db.readline()
            line_lng = len(line)
            string = ""
            if prt:
                print "read: ", i, " returns: ", line
            fil = line.split(',')
            device=         fil[0]
            ID  =           fil[1]
            model  =        fil[2]
            if  model == None:
                model = ' '
            Registration = fil[3]
            if  Registration == None or Registration == "''":
                Registration = "'NOREG'"
            cn =            fil[4]
            if  cn == None:
                cn = ' '
            i = i + 1
            if prt:
                print "Line: ", i-1, " ID: ", ID,  " Dev: ", device, " Model: ", model, " Registration: ", Registration,  " CN: ", cn
            Registration=Registration.strip(" ")
            Registration=Registration.replace(" ", "_")
            row = '\t\t%s : %s,\n' % (ID,  Registration)              # write just what we need: ID and registration
            flm_txt.write(row)
            device=device.strip("'")
            ID=ID.strip("'")
            Registration=Registration.strip("'")
            cn=cn.strip("'")
            model=model.strip("'")
            curs.execute("insert into GLIDERS values(?,?,?,?,?, ?)", (ID, Registration, cn, model, "O", device))
            if prt:
	    	print ID, Registration, cn, model
            
        except:
            print "\nNumber of rows is: ", i - 1
            return True
    return True
#
# Main logic
#
prtreq =  sys.argv[1:]
if prtreq and prtreq[0] == 'prt':
    prt = True
else:
    prt = False
conn=sqlite3.connect(config.DBpath+config.DBname)
curs=conn.cursor()
curs.execute("delete from GLIDERS")             # delete all rows

print "Start build OGN file from OGN database"
t1 = time.time() 
ogndb(prt, curs)
t2 = time.time()
print "End build OGN DB in ", t2 - t1 , " seconds"
conn.commit()
