#!/usr/bin/env python
#
# Program to read flarm_id database and create a file as the base for known gliders
#

import sys
sys.path.insert(0, '/var/www/html')
import config

import string
import requests
import time
import sqlite3

print config.DBname

dbpath=r'/nfs/OGN/SWdata/'

def flarmdb (prt, curs):
    cin=0
    cout=0 
    dups=0   
    
    db      = open("flarmdata.fln", 'r')
    flm_txt = open("flarmdata.txt", 'w')
    # Read first line and convert to number
    x = db.readline()
    val = int(x, 16)
    print "First line from FlarmNet data is : ", val
    
    i = 1
    line = ""
    nos_lines = val 
    while True:
        try:
            line = db.readline()
	    if not line:
		print cin, cout
		return True
            line_lng = len(line)
	    cin +=1
            string = ""
#            print "read: ", i, " returns: ", line
            for j in range(0,172,2):
#            for j in range(0,line_lng - 1,2):
    #            x = line[j:j+2]
    #            y = int(x, 16)
    #            c = chr(y)
                c = chr(int(line[j:j+2],16))
                string = string + c
            i = i + 1
            ID = str(string[0:6]).decode("iso-8859-15").encode("utf-8")
            try:
                Airport = str(string[27:47]).decode("utf-8").encode("iso-8859-15")
                Airport = Airport.rstrip()
            except:
                print "Code error at Airport name:", str(string[27:47])
                Airport='None'
            try:
            	Type = str(string[48:69]).decode("iso-8859-15").encode("utf-8")
            except:
                print "Code error at Type:", str(string[48:69])
                Type='None'
            Registration = str(string[69:75]).decode("iso-8859-15").encode("utf-8")
            Registration=Registration.strip("'")
            Registration=Registration.strip(" ")
            Registration=Registration.replace(" ", "_")

            try:
            	Radio = str(string[79:86]).decode("iso-8859-15").encode("utf-8")
            except:
                print "Code error at Radio:", str(string[79:86])
                Radio='None'
            if prt:
                    print "Line: ", i-1, " ID: ", ID,  " Airport: ", Airport, " Type: ", Type, " Registration: ", Registration,  " Radio: ", Radio
            row = '\t\t"%s":"%s",\n' % (ID,  Registration)              # write just what we need: ID and registration
            ID=ID.strip("'")
            Registration=Registration.strip("'")
            Type=Type.strip("'")
	    try:
            	curs.execute("insert into GLIDERS values(?,?,?,?,?,?)", (ID, Registration, " ", Type, "F", "F"))
                flm_txt.write(row)
		cout += 1
            except:
		dups+=1
                #print "Duplicate ID on DB:", ID, Registration, Type, "Dup #", dups, i-1
        except:
            print "Error at row : ", i - 1
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
    
print "Start build Flarm file from Flarmnet"
t1 = time.time() 
flarmdb(prt, curs)
t2 = time.time()
print "End build Flarm DB in ", t2 - t1 , " seconds"
conn.commit()
conn.close()
