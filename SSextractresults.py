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


class WebScraper:
    """Simple web scraper for static content using requests and BeautifulSoup"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup"""
        return BeautifulSoup(html, 'html.parser')
    
    def scrape_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a page"""
        html = self.fetch_page(url)
        if html:
            return self.parse_html(html)
        return None
    
    def extract_text(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """Extract text from elements matching CSS selector"""
        elements = soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements]
    
    def extract_links(self, soup: BeautifulSoup, selector: str = 'a') -> List[str]:
        """Extract URLs from anchor tags"""
        links = []
        for link in soup.select(selector):
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute
                if self.base_url:
                    href = urljoin(self.base_url, href)
                links.append(href)
        return links
    
    def extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract image URLs and alt text"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and self.base_url:
                src = urljoin(self.base_url, src)
            images.append({
                'src': src,
                'alt': img.get('alt', '')
            })
        return images
    
    def extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """Extract data from HTML tables"""
        tables_data = []
        for table in soup.find_all('table'):
            table_data = []
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                table_data.append(row_data)
            tables_data.append(table_data)
        return tables_data
    
    def scrape_multiple_pages(self, urls: List[str]) -> List[BeautifulSoup]:
        """Scrape multiple pages"""
        results = []
        for url in urls:
            soup = self.scrape_page(url)
            if soup:
                results.append(soup)
        return results


class DynamicWebScraper:
    """Web scraper for dynamic content using Playwright (requires installation)"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.playwright = None
    
    async def setup(self):
        """Initialize Playwright browser"""
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
    
    async def scrape_page(self, url: str, wait_for: str = None) -> str:
        """Scrape a page with JavaScript rendering"""
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until='networkidle')
            if wait_for:
                await page.wait_for_selector(wait_for)
            content = await page.content()
            return content
        finally:
            await page.close()
    
    async def cleanup(self):
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# Utility functions

def save_to_json(data: Dict, filename: str):
    """Save scraped data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_to_csv(data: List[Dict], filename: str):
    """Save scraped data to CSV file"""
    if not data:
        return
    
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def save_2_csv(data: List[Dict], filename: str):
    """Save scraped data to CSV file"""
    if not data:
        return
    
    keys = data[0]
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in data:
            del row[1]
            #print(row)
            writer.writerow(row)


def scrape_table(url):
    """Example: Scrape table data"""
    
    scraper = WebScraper()
    # Example with a page containing tables
    soup = scraper.scrape_page(url)
       
    
    if soup:
        tables = scraper.extract_tables(soup)
        return (tables)        


def scrape_links(url):
    """Example: Scrape table data"""
    
    scraper = WebScraper()
    # Example with a page containing links
    soup = scraper.scrape_page(url)
       
    
    if soup:
        links = scraper.extract_links(soup)
        return (links)        



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
                 file=competition+'_'+file		# add the comp ID to distinguish between comps
                 save_to_json(table, "../SWdata/"+file+'.json')	# create a JSON file
                 save_2_csv  (table, "../SWdata/"+file+'.csv')	# and a CSV file
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
