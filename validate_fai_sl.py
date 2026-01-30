#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#
#   This function validates the FAI's sporting licenses
#
# ================================================================================================================= #

import sys
import json
import urllib.request, urllib.error, urllib.parse
import datetime
import time
import os
import math
import pycountry
import socket
def get_licenses_per_country(country,prt=True):
   licenses=[]
   start=0
   nl=100
   while nl == 100:				# while is not over ???
      url="https://extranet.fai.org/api/v1/licences?auth_username=FAIOrganizer&auth_password=czlWc3NTZXdtUg==&discipline=Gliding&country="+country+"&limit_length=100&limit_start="+str(start)
      if prt:
         print (url,"\n\n")
      j = urllib.request.urlopen(url)
      rr=j.read().decode('UTF-8') 
      j_obj = json.loads(rr)
      nl=len(j_obj)
   
      for lic in j_obj:
         if lic["Sport"] == 'Gliding':
            #print (lic)
            licenses.append(lic)
      if prt:
         print ("NL:", nl, "Start", start, "Lics", len(licenses))
      start += nl
   return (licenses)

def validate_fai_sl(country,sl=0, name=' ',prt=True):
    lpc=get_licenses_per_country(country, prt)
    if prt:
       print (len(lpc), sl, name, json.dumps(lpc, indent=4))
    if sl != 0:
       for lic in lpc:
           if lic['idlicencee'] == sl:
              return (True)
       return (False)
    elif name != ' ':
       for lic in lpc:
           if lic['surname_lip'] == name:
              return (True)
       return (False)
    else:
       return (-1)

def get_license_details_byname(country, givenname=' ', surname=' ',prt=True):
    lpc=get_licenses_per_country(country, prt)
    if prt:
       print (len(lpc), givenname, surname, "\n\n", json.dumps(lpc, indent=4))
    for lic in lpc:
        if givenname == ' ':
           if lic['surname_lip'] == surname :
              return (lic)
        else: 
           if lic['surname_lip'] == surname and lic['givenname_lip'] == givenname:
              return (lic)
    return (None)

def get_license_details_byln(country, ln, prt=True):
    lpc=get_licenses_per_country(country, prt)
    if prt:
       print (len(lpc), ln, "\n\n", json.dumps(lpc, indent=4))
    for lic in lpc:
        if lic['idlicencee'] == ln:
           return (lic)
    return (None)

def get_full_license_details(idlicence, prt=False):
    l=str(idlicence)
    url="https://extranet.fai.org/api/v1/licence/"+l+"?auth_username=FAIOrganizer&auth_password=czlWc3NTZXdtUg"
    if prt:
       print (url,"\n\n")
    j = urllib.request.urlopen(url)
    rr=j.read().decode('UTF-8') 
    j_obj = json.loads(rr)
    return(j_obj)
#################################################################
