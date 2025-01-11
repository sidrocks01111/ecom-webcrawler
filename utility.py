import json
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from urllib.parse import urlparse, unquote
import time

from dynamic_content import DynamicContentHandler

class CrawlerHelper:

    def __init__(self):
        self.product_output = {}
        self.product_url_recogniser = ProductUrlRecogniser()


    def is_product_url(self, url, soup):
        return self.product_url_recogniser.check_if_product_url(url, soup)
    
    
    def add_url_output(self, domain_url, product_url, filename='product_urls.json'):
        if domain_url not in self.product_output:
            self.product_output[domain_url] = []
        elif product_url not in self.product_output[domain_url]:
            self.product_output[domain_url].append(product_url)

        with open(filename, 'w') as outfile:
            json.dump(self.product_output, outfile, indent=4)



class ProductUrlRecogniser:
    
    def __init__(self):
        self.product_patterns = [
        r'/product/\d+', 
        r'/p/\w+/\d+',     
        r'/[\w-]+/\d+$',
        r'/item/', 
        r'/itm/'   
    ]
    def check_if_product_url(self, url, soup):
        if self.check_in_existing_patterns(url):
            return True
        
        if self.find_product_elements(soup):
            self.extract_url_pattern(url)
            return True
    
    def check_in_existing_patterns(self, url):
        for pattern in self.product_patterns:
            if re.search(pattern, url):
                print("URL matches a known product pattern.")
                return True, pattern
            
    def find_product_elements(self, soup):
        price_pattern = r'[\d,.]+( USD|€|₹|etc.)'  # Adjust currency symbols as needed
        description_keywords = ['description', 'buy', 'cart', 'shipping', 'review']
        
        price = soup.find(string=re.compile(price_pattern))
        if not price:
            return False
    
        for keyword in description_keywords:
            if soup.find(string=re.compile(keyword, re.I)):
                return True
    
        return False
    
    def extract_url_pattern(url):
        match = re.search(r'(/[\w-]+/\d+)', url)
        if match:
            return match.group(0)
        return None