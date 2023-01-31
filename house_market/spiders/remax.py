import scrapy
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from time import sleep
import os


def iniciar_driver():
    chrome_options = Options()
    LOGGER.setLevel(logging.WARNING)
    arguments = ['--lang=pt-BR', '--window-size=1920,1080',
                 '--headless', '--disable-gpu', '--no-sandbox']

    for argument in arguments:
        chrome_options.add_argument(argument)

    chrome_options.add_experimental_option('prefs', {
        'download.prompt_for_download': False,
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_setting_values.automatic_downloads': 1,

    })
    driver = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(
        driver,
        10,
        poll_frequency=0.5,
        ignored_exceptions=[
            NoSuchElementException,
            ElementNotVisibleException,
            ElementNotSelectableException,
        ]
    )
    return driver, wait


class RemaxBotSpider(scrapy.Spider):
    allowed_domains = ['remax.pt']
    name = 'remaxbot'

    def start_requests(self):
        urls = []

        absolute_path = os.path.dirname(__file__)
        relative_path = "../../domains.txt"
        domain_path = os.path.join(absolute_path, relative_path)

        for line in open(domain_path, 'r').readlines():
            urls.append(line.replace('%22', '"'))

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'next_url': urls[0]})

    # custom_settings = {
    #     'FEEDS': {'datas.csv': {'format': 'csv'}}
    # }

    def parse(self, response):
        driver, wait = iniciar_driver()
        driver.get(response.meta["next_url"])

        page_arrow_path = "//li[@class='arrow page-item'][1]/a"

        while True:
            results = driver.find_elements(
                By.XPATH, "//div[@class='col-12 col-sm-6 col-md-6 col-lg-4 col-xl-3 result']")

            for result in results:
                try:
                    link = result.find_element(
                        By.XPATH, ".//div[@class='listing-search-searchdetails-component']/a").get_attribute('href')
                except:
                    link = "--"
                try:
                    image = result.find_element(
                        By.XPATH, ".//div/div[@class='listing-picture']/figure/picture/img").get_attribute('src')
                except:
                    image = "--"
                try:
                    price = result.find_element(
                        By.XPATH, ".//div[@class='figCaption']/p[@class='listing-price']").text
                except:
                    price = "--"
                try:
                    address = result.find_element(
                        By.XPATH, ".//div[@class='listing-body']/h2[@class='listing-address']/span").text
                except:
                    address = "--"
                try:
                    type = result.find_element(
                        By.XPATH, ".//ul[@class='listing-footer']/li[@class='listing-type']").text
                except:
                    type = "--"
                try:
                    area = (result.find_element(
                        By.XPATH, ".//li[@class='listing-area']").text).replace("\n2", format('\u00B2'))
                except:
                    area = "--"
                try:
                    bathroom = result.find_element(
                        By.XPATH, ".//li[@class='listing-bathroom']").text
                except:
                    bathroom = "--"
                try:
                    bedroom = result.find_element(
                        By.XPATH, ".//li[@class='listing-bedroom']").text
                except:
                    bedroom = "--"

                yield {
                    "link": link,
                    "image": image,
                    "price": price,
                    "address": address,
                    "type": type,
                    "area": area,
                    "bathroom": bathroom,
                    "bedroom": bedroom,
                }

            try:
                next_page_arrow = driver.find_element(
                    By.XPATH, page_arrow_path)
            except NoSuchElementException:
                break

            driver.execute_script(
                'arguments[0].click()', next_page_arrow)

            page_arrow_path = "//li[@class='arrow page-item'][2]/a"

            sleep(2)
        driver.close()
