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
        poll_frequency=1,
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
        urls = ['https://remax.pt/comprar?searchQueryState=%7B"regionName":"","sort":%7B"fieldToSort":"ContractDate","order":1%7D,"businessType":1,"listingClass":1,"page":1,"t":"","mapIsOpen":false,"mapScroll":false,"searchNextToMe":false,"listingTypes":%5B%5D%7D']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'next_url': urls[0]})

    def parse(self, response):
        driver, wait = iniciar_driver()
        driver.get(response.meta["next_url"])

        results = driver.find_elements(
            By.XPATH, "//div[@class='col-12 col-sm-6 col-md-6 col-lg-4 col-xl-3 result']")

        for result in results:
            yield {
                "link": result.find_element(By.XPATH, ".//div[@class='listing-search-searchdetails-component']/a").get_attribute('href'),
                "image": result.find_element(By.XPATH, ".//div/div[@class='listing-picture']/figure/picture/source[@media='(min-width: 376px) and (max-width: 750px)']").get_attribute('srcset'),
                "price": result.find_element(By.XPATH, ".//div[@class='figCaption']/p[@class='listing-price']").text,
                "address": result.find_element(By.XPATH, ".//div[@class='listing-body']/h2[@class='listing-address']/span").text,
                "type": result.find_element(By.XPATH, ".//ul[@class='listing-footer']/li[@class='listing-type']").text,
                "area": result.find_element(By.XPATH, ".//li[@class='listing-area']").text,
                "bathroom": result.find_element(By.XPATH, ".//li[@class='listing-bathroom']").text,
                "bedroom": result.find_element(By.XPATH, ".//li[@class='listing-bedroom']").text,
            }

        try:
            next_page_url = response.xpath("//li[@class='next']/a/@href").get()
            if next_page_url is not None:
                next_url = response.urljoin(next_page_url)
                yield scrapy.Request(url=next_url, callback=self.parse)
        except:
            print("Last page...")

        driver.close()


def get_remax_url():
    pass
