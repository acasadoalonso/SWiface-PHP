#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# This program eithe serach or validate a pilot's FAI Sporting license
#
# Author: Angel Casado - January 202r62
#
import sys
import os
import argparse
import config
import iso2ioc
# -*- coding: UTF-8 -*-

from validate_fai_sl import *
#################################################################
def display_pilot_license(r,  web=True, full=False):
    html1 = """<TITLE>SearchFASL</TITLE> <IMG src="gif/FAIgliding.jpeg" border=1 alt=[image]><H1> <Extracted flight</H1>  """
    if web:
       print (html1)
    print ("IOC:",                   r['IOC'])
    print ("Is_expired:",            r['is_expired'])
    #print ("License Number:",        r['idlicence'])
    print ("FAI ID:",                r['idlicencee'])
    print ("License number by NAC:", r['licencenumber_lic'])
    print ("Givenname:",             r['givenname_lip'])
    print ("Surname:",               r['surname_lip'])
    print ("Birthdate:",             r['birthdate_lip'])
    print ("Gender:",                r['gender_lip'])
    print ("Date issued:",           r['dateissued_lic'])
    print ("Valid until:",           r['validuntil_lic'])
    full=True
    if full:
       r=get_full_license_details(r['idlicence'], prt=False)
       #print("Full License details:", r, "\n\n")
       print ("Country:",            r['idlicencecountry_lip'])
       print ("Nationality Country:",r['idnationality_lip'])
       print ("Residence Country:",  r['idresidencecountry_lip'])
    return

# ======================================================================================================================= #
#                            Search for FAI Sporting license
# ======================================================================================================================= #

pgmver='1.0'
# ---------------------------------------------------------------- #
# ======================== parsing arguments =======================#
parser = argparse.ArgumentParser(description="SAR4comp utility ")
parser.add_argument('-c', '--country', required=True,	# IOC Country code
                    dest='country', action='store', default='')
parser.add_argument('-n', '--pilotname', required=False,
                    dest='pilotname', action='store', default='')
parser.add_argument('-s', '--sportinglicense', required=False,
                    dest='sportinglicense', action='store', default='0')
parser.add_argument('-p', '--print',  required=False,
                    dest='prt',    action='store', default=False)
parser.add_argument('-w', '--web',  required=False,
                    dest='web',    action='store', default=False)

args      = parser.parse_args()
country   = args.country				# IOC country code
pilotname = args.pilotname    				# Pilot name
if args.sportinglicense.isnumeric():
   sl        = int(args.sportinglicense) 		# Pilot sportinglicense
else:
   sl        = 0
prt       = args.prt					# print on|off
web       = args.web					# web on|off

#
#
# ----------------------------------------------------------------------
if 'USER' in os.environ:
        user=os.environ['USER']
else:
        user="www-data"                     		# assume www
# ----------------------------------------------------------------------

if not web:
   print("\n\n")
   print("Program to search or validate a pilot's FAI Sporting license ", pgmver)
   print("===========================================================================================================")
   print("Args  IOC Country: ", country, "Pilot name: ", pilotname, "SL:", sl, prt, web, user)
else:
   prt=False

# ======================== SETUP parameters =======================#
#
if country == '':
   print ("IOC country is mandatory\n\n")
   exit (-1)
if country not in iso2ioc.IOC:
   print ("Not a valid IOC country code ...", country)
   exit (-2) 
if sl != 0:
   r=validate_fai_sl(country, sl=sl, prt=False)
   if r:
      print ("\n\n",sl, " is a valid FAI's license.\n\n")
   r=get_license_details_byln(country, sl,  prt=False)
   if r != None:
      display_pilot_license(r, web)
   else:
      print ("\n\nLicense number not found ...\n\n")
if pilotname != '':
   r=validate_fai_sl(country, name=pilotname, prt=False)
   if r:
      print ("\n\n",pilotname, " is a valid surname for country ", country, "with a valid sporting license.\n\n")
   r=get_license_details_byname(country, surname=pilotname,  prt=False)
   if r != None:
      display_pilot_license(r, web)
   else:
      print ("\n\nPilot namme not found ...\n\n")

exit(0)
