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
Initials                = cfg.get('server', 'Initials').strip("'").strip('"')


datafile.write("DBpath='"+DBpath+"' \n")
datafile.write("DBhost='"+DBhost+"' \n")
datafile.write("DBuser='"+DBuser+"' \n")
datafile.write("DBname='"+DBname+"' \n")
datafile.write("DBpasswd='"+DBpasswd+"' \n")
datafile.write("Initials='"+Initials+"' \n")
datafile.write("MySQL="+MySQLtext+" \n")
# --------------------------------------#
datafile.write(tailfile.read())
datafile.close()
tailfile.close()

