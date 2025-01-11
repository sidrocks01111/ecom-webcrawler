
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from config import current_directory_path


class DynamicContentHandler:

    def __init__(self):
        # self.driver = webdriver.Chrome(current_directory_path + 'driver/chromedriver')
        chrome_driver_path = '/Users/siddharth.singh/Desktop/test/shoppin/web_crawler/driver/chromedriver'
        service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=service)
        self.driver_wait = WebDriverWait(self.driver, 1)
    

    async def crawl_dynamic_content(self, url):

        self.driver.get(url)
        last_page_height = 0
        match = False
        if_new_page = True
        all_urls = set()
        while match is False:
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            try:
                self.driver_wait.until(lambda drv: self.driver.execute_script("return document.documentElement.scrollHeight;") > last_page_height)
                # self.scraper.scrape(self.driver.page_source, new_page=if_new_page)
                if_new_page = False
                urls = await self.extract_urls_from_page(page_source=self.driver.page_source)
                new_urls = set(urls) - all_urls
                all_urls.update(new_urls)

                # If no new URLs were added, stop crawling
                if len(new_urls) == 0:
                    match = True
            except TimeoutException:
                print("Cannot scroll down more. Checking if there is pagination...")

                # next_buttons = [elem for elem in self.driver.find_elements_by_xpath("//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'next')]") if elem.tag_name != 'script']
                next_buttons = [elem for elem in self.driver.find_elements(By.XPATH, "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'next')]") if elem.tag_name != 'script']

                if next_buttons:
                    print("Clicking next button")
                    self.driver.execute_script("arguments[0].click();", next_buttons[0])
                    if_new_page = True

                else:
                    print("Cannot find pagination. Exiting...")
                    match = True

            if not match:

                if if_new_page:
                    last_page_height = 0
                else:
                    last_page_height = self.driver.execute_script("return document.documentElement.scrollHeight;")

            else:

                print("Scraping complete. Exiting...")
        return list(all_urls)

    async def extract_urls_from_page(self, page_source):
        soup = BeautifulSoup(page_source, 'html.parser')
        urls = []
        for a_tag in soup.find_all('a', href=True):
            url = a_tag['href']
            # If the URL is relative, make it absolute
            if not url.startswith("http"):
                url = 'http://' + url.lstrip('/')
            urls.append(url)

        return urls



# class Scraper:

#     def __init__(self):
#         self.output = []
#         self.current_page_index = -1
#         self.total_items = sum([len(page_items) for page_items in self.output])

#     def scrape(self, page_source, new_page=False):

#         if new_page or self.current_page_index is -1:
#             self.current_page_index += 1
#             self.output.append([])

#         self.output[self.current_page_index] += self.html_lib.elements_attribute_map(page_source, from_index=len(self.output[self.current_page_index]))

#         self.total_items = sum([len(page_items) for page_items in self.output])

#     def process_output(self):

#         concatenated_output = []
#         for result in self.output:
#             concatenated_output += result
#         print(len(concatenated_output))
#         all_keys = []
#         result_keys = [result.keys() for result in concatenated_output]

#         for result_key in result_keys:

#             for key in result_key:
#                 if key not in all_keys:
#                     all_keys.append(key)

#         all_keys = set(all_keys)

#         for result in concatenated_output:
#             for key in all_keys:
#                 if key not in result:
#                     result[key] = ''

#         for output in concatenated_output:

#             for key in output:
#                 print(key),
#                 print(": "),
#                 print(output[key]),

#             print("")

#         # write_to_excel(concatenated_output, all_keys)


# # # auto_crawl("http://www.amazon.in/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=iphone")