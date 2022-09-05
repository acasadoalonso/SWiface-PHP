#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# This program collect data form SoaringSpot/SGP/Directory IGC files and rebuild a flight track based on the FLARM info contained on the IGC files
#
# Author: Angel Casado - January 2022
#
import sys
import os
import argparse

import config
#from config import *

# ======================================================================================================================= #
#                            SAR4comp 
# ======================================================================================================================= #
pgmver='2.0'
reposerver="acasado.es:60080/SWS/SWdata/"
html1 = """<TITLE>SAR4comp</TITLE> <IMG src="gif/FAIgliding.jpeg" border=1 alt=[image]><H1> <Extracted flight</H1>  """
html2 = """<center><table><tr><td><pre>"""
html3 = """</pre></td></tr></table></center>"""
html4 = 'Click here to see the resulting file ==> <a href="http://cunimb.net/igc2map.php?lien=http://' + reposerver+'%s'
# ---------------------------------------------------------------- #
# ======================== parsing arguments =======================#
parser = argparse.ArgumentParser(description="SAR4comp utility ")
parser.add_argument('-t', '--type', required=True,	# type SOA|SGP|DIR
                    dest='type', action='store', default='')
parser.add_argument('-c', '--client', required=False,
                    dest='client', action='store', default='')
parser.add_argument('-s', '--secret', required=False,
                    dest='secret', action='store', default='')
parser.add_argument('-f', '--flarm', required=False,
                    dest='flarm', action='store', default='')
parser.add_argument('-i', '--indexday', required=False,
                    dest='indexday', action='store', default='0')
parser.add_argument('-g', '--sgpid', required=False,
                    dest='sgpid', action='store', default='0')
parser.add_argument('-p', '--print',  required=False,
                    dest='prt',    action='store', default=False)
parser.add_argument('-w', '--web',  required=False,
                    dest='web',    action='store', default=False)
args      = parser.parse_args()
reqtype   = args.type					# request type SOA|SGP|DIR
client    = args.client    				# client ID
secretkey = args.secret  				# secret key
flarm     = args.flarm 					# flarm ID
indexday  = args.indexday				# indexday ID
sgpid     = args.sgpid  				# indexday ID
prt       = args.prt					# print on|off
web       = args.web					# web on|off
if indexday.isdigit():          			# if provided and numeric
    idx = int(indexday)         			# index day
else:
    idx = 0

if sgpid.isdigit():          				# if provided and numeric
    sgpid = int(sgpid)         				# SGP event ID
else:
    sgpid = 0

if flarm == '':
   extractopt=False
else:
   extractopt=True
#
if not web:
   print("\n\n")
   print("Utility extract IGC files from SoaringSpot/SGP/DIR and rebuild a flight track based on the FLARM info ", pgmver)
   print("===========================================================================================================")
   print("Args:", reqtype, client, secretkey, flarm, indexday, sgpid, prt, web)
else:
   prt=False
resultfile=''						# name of the resulting file

# ======================== SETUP parameters =======================#
if reqtype == "SOA":					# extracting IGC file form SoaringSpot
   from soa2filfuncs import soa2fil			# get the routines
   # validate the arguments
   # where to find the clientid and secretkey files
   if (client == '' and secretkey == '') or (client == '0' and secretkey == '0'):    		# if not provided in the arguments ???
       if config.clientid == '' or config.secretkey == '': # check if provided by the config file ???
           if prt:
               print("Reading the clientid/secretkey from the SoaringSpot directory")
           # if client/screct keys are not in the config file, read it for SoaringSpot directory
           cwd = os.getcwd()                  		# get the current working directory
           secpath = cwd+"/SoaringSpot/"
           f = open(secpath+"clientid") 		# open the file with the client id
           client = f.read()               		# read it
           client = client.rstrip() 			# clear the whitespace at the end
           f = open(secpath+"secretkey") 		# open the file with the secret key
           secretkey = f.read()            		# read it
           						# clear the whitespace at the end
           secretkey = secretkey.rstrip().encode(encoding='utf-8')
       else:						# the credentials are from the config file
           client = config.clientid
           client = client.rstrip() 			# clear the whitespace at the end
           secretkey = config.secretkey
           secretkey = secretkey.rstrip().encode(encoding='utf-8')
   else:						# use the clientid and secretkey from the arguments
       client = client.rstrip() 			# clear the whitespace at the end
       client = client.replace('\\', '')
       secretkey = secretkey.replace('\\', '')
       secretkey = secretkey.rstrip().encode(encoding='utf-8')
   #print (client,":::",secretkey)
							# call the routines
   resultfile=soa2fil(client,secretkey,idx,flarm,extractopt,prt,web)

elif reqtype == "SGP":					# extracting the IGC files from the sgp.aero website
   from sgp2filfuncs import sgp2fil			# get the routines
   resultfile=sgp2fil(sgpid,idx,flarm,extractopt,prt,web)	# call the routines

elif reqtype == "DIR":					# extracting the IGC files from the DIR directory
   from dir2filfuncs import dir2fil			# get the routines
   resultfile=dir2fil(flarm,prt,web)			# call the routinesa

else:
   print ("\nInvalid request type !!!\n")		# it is not a valid request

if web:
   print (html1)
   print (html2)
   fn    = (html4 % resultfile.lstrip())		# URL
   fname = ("FN:%-33s" % resultfile)    		# prepare the filename
   print(fn, '">MAP</a>', "<a>", fname, " </a>")
   print (html3)
else:
   print ("The resulting file is:", resultfile)		# result the name of the file
exit(0)