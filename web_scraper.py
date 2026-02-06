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


