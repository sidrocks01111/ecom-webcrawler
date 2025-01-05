import json
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from urllib.parse import urlparse, unquote
import time


class CrawlerHelper:

    def __init__(self):
        self.product_patterns = [r'/product/', r'/item/', r'/itm/']
        self.exclude_patterns = [
        r'/blog',
        r'/documentation',
        r'/how-to-video',
        r'/test-sites',
        r'/buyagain'
    ]
        self.product_output = {}


    def is_product_url(self, url):
        return any(pattern in url for pattern in self.product_patterns) and not any(pattern in url for pattern in self.exclude_patterns)
    
    
    def add_url_output(self, domain_url, product_url, filename='product1_urls.json'):
        if domain_url not in self.product_output:
            self.product_output[domain_url] = []
        elif product_url not in self.product_output[domain_url]:
            self.product_output[domain_url].append(product_url)

        with open(filename, 'w') as outfile:
            json.dump(self.product_output, outfile, indent=4)

    def handle_dynamic_content(self, url):
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        # Scroll to load dynamic content
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        html = driver.page_source
        driver.quit()
        return html

