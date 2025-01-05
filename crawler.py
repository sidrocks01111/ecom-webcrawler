
import asyncio
import httpx
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

from queue import Queue

from validators import Validator
from utility import *

R = '\033[31m'  
G = '\033[32m'  
W = '\033[0m'   
C = '\033[96m'

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO
)



class Crawler:
    def __init__(self, urls, crawl_helper: CrawlerHelper, max_depth=3, max_threads=10):
        self.visited_urls = set()
        self.urls_queue = Queue()
        self.initialise_queue(urls)
        self.crawl_helper = crawl_helper
        self.max_depth = max_depth
        self.max_threads = max_threads
        self.client = httpx.AsyncClient(verify=False,limits=httpx.Limits(max_keepalive_connections=5, max_connections=10))

    def initialise_queue(self, urls):
        for url in urls:
            self.urls_queue.put((url, 0))

    async def download_url(self, url):
        response = await self.client.get(url)
        return response.text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and not path.startswith(('#', 'javascript:', 'mailto:')):
                if self.crawl_helper.is_product_url(url):
                    match = re.search(r'^.*?\.[a-zA-Z0-9]+', path)
                    if match:
                        domain_url = match.group(0)
                        self.crawl_helper.add_url_output(domain_url, product_url=url)
                    continue
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url, depth):
        if url and url not in self.visited_urls and depth <= self.max_depth:
            self.urls_queue.put((url, depth))

    async def crawl(self, url, depth):
        if not Validator.validate_url(url):
            logging.warning(f"Skipping invalid URL: {url}")
            return
        html = await self.download_url(url)
        if html is None:
            self.crawl_helper.handle_dynamic_content(url)
        for linked_url in self.get_linked_urls(url, html):
            self.add_url_to_visit(linked_url, depth + 1)

        
    async def process_url(self, url, depth):
        if url is None:
            return
        logging.info(f'{C}Crawling: {url} (Depth: {depth}){W}')
        try:
            await self.crawl(url, depth)
        except httpx.RequestError as e:
            logging.error(f'{R}Failed to crawl: {url} - {e}{W}')
        except Exception as e:
            logging.exception(f'{R}Failed to crawl: {url} - {e}{W}')
        finally:
            self.visited_urls.add(url)
    async def run(self):
        tasks = []
        while not self.urls_queue.empty():
            for _ in range(min(self.urls_queue.qsize(), self.max_threads)):  # Process up to 10 URLs concurrently
                url, depth = self.urls_queue.get()
                task = asyncio.create_task(self.process_url(url, depth))
                tasks.append(task)
            await asyncio.gather(*tasks)
            tasks.clear()




if __name__ == '__main__':
    urls_to_scrape = input("Enter list of URLs to scrape ex: url1,url2: ")
    max_depth = int(input("Enter Max depth: "))
    max_threads = int(input("Enter Max threads: "))
    urls = urls_to_scrape.split(",")
    crawl_helper = CrawlerHelper()
    crawler = Crawler(urls, crawl_helper, max_depth=max_depth, max_threads=max_threads)
    asyncio.run(crawler.run())