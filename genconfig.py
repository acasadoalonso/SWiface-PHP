#!/usr/bin/python
#
# configuration for the Silent Wings OGN interface the online part
#

#-------------------------------------
# OGN-Silent Wings interface --- Settings
#-------------------------------------
#
#-------------------------------------
# Setting values from config.ini file
#-------------------------------------
#
import socket
import os
import datetime
from configparser import ConfigParser
datafile = open("config.py", "w")
tailfile = open("configtail.txt", "r")
datafile.write("# SWS configuration file \n")

hostname=socket.gethostname()
datafile.write("# SWS hostname: "+hostname+"\n")
datafile.write("# Config generated: "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" \n")
cfg=ConfigParser()
cfg.read('/etc/local/SWSconfig.ini')

DBpath                  = cfg.get('server', 'DBpath').strip("'").strip('"')
MySQLtext               = cfg.get('server', 'MySQL').strip("'").strip('"')
DBhost                  = cfg.get('server', 'DBhost').strip("'").strip('"')
DBuser                  = cfg.get('server', 'DBuser').strip("'").strip('"')
DBpasswd                = cfg.get('server', 'DBpasswd').strip("'").strip('"')
DBname                  = cfg.get('server', 'DBname').strip("'").strip('"')
SQLite3                 = cfg.get('server', 'SQLite3').strip("'").strip('"')
Initials                = cfg.get('server', 'Initials').strip("'").strip('"')

eventname1              = cfg.get('location', 'eventname1').strip("'").strip('"')
eventname2              = cfg.get('location', 'eventname2').strip("'").strip('"')

eventdesc1              = cfg.get('location', 'eventdesc1').strip("'").strip('"')
eventdesc2              = cfg.get('location', 'eventdesc2').strip("'").strip('"')

datafile.write("DBpath='"+DBpath+"' \n")
datafile.write("DBhost='"+DBhost+"' \n")
datafile.write("DBuser='"+DBuser+"' \n")
datafile.write("DBname='"+DBname+"' \n")
datafile.write("SQLite3='"+SQLite3+"' \n")
datafile.write("DBpasswd='"+DBpasswd+"' \n")
datafile.write("MySQL="+MySQLtext+" \n")
datafile.write("Initials='"+Initials+"' \n")
datafile.write("eventname1='"+eventname1+"' \n")
datafile.write("eventname2='"+eventname2+"' \n")
datafile.write("eventdesc1='"+eventdesc1+"' \n")
datafile.write("eventdesc2='"+eventdesc2+"' \n")
# --------------------------------------#
datafile.write(tailfile.read())
datafile.close()
tailfile.close()
