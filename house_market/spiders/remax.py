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
        urls = ['https://remax.pt/comprar?searchQueryState=%7B"regionName":"Lisboa","sort":%7B"fieldToSort":"ContractDate","order":1%7D,"businessType":1,"listingClass":1,"page":1,"t":"","mapIsOpen":false,"mapScroll":false,"searchNextToMe":false,"listingTypes":%5B"11"%5D,"price":%7B"min":null,"max":100000%7D,"prn":"Lisboa","regionID":"76","regionType":"Region1ID","regionCoordinates":%7B"latitude":38.8404598668955,"longitude":-9.2186952991834%7D,"regionZoom":9%7D']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'next_url': urls[0]})

    def parse(self, response):
        driver, wait = iniciar_driver()
        driver.get(response.meta["next_url"])

        page_arrow_path = "//li[@class='arrow page-item'][1]/a"

        while True:
            results = driver.find_elements(
                By.XPATH, "//div[@class='col-12 col-sm-6 col-md-6 col-lg-4 col-xl-3 result']")

            for result in results:
                yield {
                    "link": result.find_element(By.XPATH, ".//div[@class='listing-search-searchdetails-component']/a").get_attribute('href'),
                    "image": result.find_element(By.XPATH, ".//div/div[@class='listing-picture']/figure/picture/img").get_attribute('src'),
                    "price": result.find_element(By.XPATH, ".//div[@class='figCaption']/p[@class='listing-price']").text,
                    "address": result.find_element(By.XPATH, ".//div[@class='listing-body']/h2[@class='listing-address']/span").text,
                    "type": result.find_element(By.XPATH, ".//ul[@class='listing-footer']/li[@class='listing-type']").text,
                    "area": (result.find_element(By.XPATH, ".//li[@class='listing-area']").text).replace("\n2", format('\u00B2')),
                    "bathroom": result.find_element(By.XPATH, ".//li[@class='listing-bathroom']").text,
                    "bedroom": result.find_element(By.XPATH, ".//li[@class='listing-bedroom']").text,
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


def get_remax_url():
    # Selenium apply available filters - return optimized url
    pass


def check_if_exists(xpath, driver):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True
