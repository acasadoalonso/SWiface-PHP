"""
Web Scraper - Multiple approaches for scraping web pages
Supports both static and dynamic content scraping
"""

import requests
import bs4
from bs4 import BeautifulSoup
import json
import csv
import sys
import os
import config
import argparse
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from web_scraper import *

if __name__ == '__main__':

# ======================================================================================================================= #
#                            Search for the final results on a Soaring Spot competition create an CSV file
# ======================================================================================================================= #

    pgmver='1.0'
# ---------------------------------------------------------------- #
    reposerver=config.SWSserver+'SWdata/'		# the server is defined on the config.py built by the genconfig.py script
    html1 = """<TITLE>SSextract</TITLE> <IMG src="gif/FAIgliding.jpeg" border=1 alt=[image]></br><H1> <Extracted results</H1>  """
    html2 = """<center><table><tr><td><pre><H1>Results from Soaring Spot: </H1></br> """
    html3 = """</pre></td></tr></table></center>"""

# ======================== parsing arguments =======================#
    parser = argparse.ArgumentParser(description="Extract results from SoaringSpot ")
    parser.add_argument('-c', '--competition', required=True,	# Competition name on SS
                       dest='competition', action='store', default='')
    parser.add_argument('-p', '--print',  required=False,
                       dest='prt',    action='store', default=False)
    parser.add_argument('-w', '--web',  required=False,
                       dest='web',    action='store', default=False)

    args       = parser.parse_args()
    competition= args.competition				# SS compatition
    prt        = args.prt					# print on|off
    web        = args.web					# web on|off

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
      print("Program to print/gen an excel file with the data from the SoaringSpot finale results on a competition", pgmver)
      print("===========================================================================================================")
      print("Args  competition: ", competition, " -->", prt, web, user)
    else:
      print(html1)
      print(html2)
      prt=False

# ======================== SETUP parameters =======================#

    baseurl='https://www.soaringspot.com/en_gb/'+competition 	# this is the base URL of SS plus the competition ID
    if prt:
       print ("Base URL:", baseurl)
    tables=scrape_table(baseurl)			# acrpe the initial result table
    links=scrape_links(baseurl)				# and get all the links
    index=14						# at link 14 start the final results
    
    for i, table in enumerate(tables):
        sclass=table[0]
        if prt:
           print(f"\nWinners Class:", sclass[0])	# get all the winners
           #print (table)
           for row in table[1:]:
               print(row)
           print ("===================\n\n")
        url="https://www.soaringspot.com"+links[index]  # get the links to the results page 
        url=url.replace(' ', '')			# delete the spaces
        file=sclass[0].replace(' ', '_')		# replace blanks with underscore
        #print ("URL:", index, url, file)
        index +=1					# for next class
        tables=scrape_table(url)			# get the results for an specific class
        for i, table in enumerate(tables):
             #print(f"\nTable {i+1}:")
             if file != '':
                 file="../SWdata/"+competition+'_'+file	# add the comp ID to distinguish between comps
                 if  os.path.isfile  (file+'.json'):
                     os.system('rm  '+file+'.json')     # remove the previous one
                 if  os.path.isfile  (file+'.csv'):
                     os.system('rm  '+file+'.csv')      # remove the previous one

                 save_to_json(table, file+'.json')	# create a JSON file
                 save_2_csv  (table, file+'.csv')	# and a CSV file
                 if web:				# if on the web prepare the html line
                    html4 = 'Click here to dowload the resulting file ==> Class: '+sclass[0]+' <a href=' + reposerver+file+'.csv> '+file+" </a>"
                    print (html4)

             if prt:					# if just print 
                for row in table:
                    print(row)
                print ("===================\n\n")
    if web:						# finish the end table html
        print (html3)
    exit()
