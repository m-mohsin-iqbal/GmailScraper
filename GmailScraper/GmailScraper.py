import time
from datetime import datetime
from selenium import webdriver
from functools import partial
import re
from pathlib import Path
import logging
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import gspread

BASE_DIR = Path(__name__).absolute().parent
print("Base dir {}".format(BASE_DIR))


class TaskLogger:

    def __init__(self, logger, extra):
        self.info = partial(logger.info, extra=extra)
        self.debug = partial(logger.debug, extra=extra)
        self.error = partial(logger.error, extra=extra)


class GmailScraper():
    base_url = 'https://mail.google.com/mail/u/0/#inbox/'
    employee_id = []

    def __init__(self):
        logs_dir = BASE_DIR / "logs"
        logs_dir.mkdir(exist_ok=True)
        logger = logging.getLogger(__name__)
        sh = logging.StreamHandler()
        log_format = "%(levelname)s : %(asctime)s : %(message)s"
        formatter = logging.Formatter(log_format)
        sh.setFormatter(formatter)
        fh = logging.FileHandler(
            logs_dir / f"{datetime.now().strftime('%Y-%m-%d %I.%M %p')}.log", mode="w"
        )
        fh.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(sh)
        logger.addHandler(fh)
        self.logger = logger
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-setuid-sandbox')
        self.options.add_argument("--proxy-server='direct://")
        self.options.add_argument('--proxy-bypass-list=*')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-accelerated-2d-canvas')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument("start-maximized")

        # self.options.add_argument('--headless')
        # self.options.add_argument("-incognito")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.base_url = "https://mail.google.com/mail/u/0/#inbox/"

    def create_driver(self):
        try:

            chrome_options = Options()
            # chrome_options.add_argument('--proxy-server=%s' % PROXY)
            chrome_options.add_argument("--user-data-dir={}/cd".format(BASE_DIR))
            driver = webdriver.Chrome(options=chrome_options)
        except:
            driver = None

        return driver

    def close_driver(self, driver):
        """
        :param driver:
        :return:
        """
        try:
            driver.close()
            driver.quit()
            print('Driver closed successfully.')
        except Exception as e:
            print(e)
            pass

    def get_element_text(self, driver, selector):
        try:
            return self.driver.find_element_by_css_selector(selector).text
        except NoSuchElementException as e:
            self.logger.info(e)
            return ''

    def get_elements(self, driver, selector):
        try:
            return driver.find_elements_by_css_selector(selector)
        except NoSuchElementException as e:
            self.logger.info(e)
            return ''

    def get_element(self, driver, selector):
        try:
            return driver.find_element_by_css_selector(selector)
        except NoSuchElementException as e:
            self.logger.info(e)
            return ''

    @staticmethod
    def make_request(driver, url):
        """
        :param driver: selenium driver
        :param url: url to hit
        :return: driver containing source of given url
        """
        if driver and url:
            url = url if not isinstance(url, bytes) else url.decode('utf-8')
            time.sleep(2)
            driver.get(url)
            return driver
        return None

    def get_index(self, lst, index, default=''):
        """
        return element on given index from list
        :param lst: list from which we will return element
        :param index: index of element
        :param default: return value if index out of range
        :return:
        """
        return lst[index] if isinstance(lst, list) and len(lst) > index else default

    def get_dict_value(self, data, key_list, default=''):
        """
        gets a dictionary and key_list, apply key_list sequentially on dictionary and return value
        :param data: dictionary
        :param key_list: list of key
        :param default: return value if key not found
        :return:
        """
        for key in key_list:
            if data and isinstance(data, dict):
                data = data.get(key, default)
            elif data and isinstance(data, list):
                data = self.get_index(data, key) if isinstance(key, int) else default
            else:
                return default
        return data

    def parse(self):
        driver = self.create_driver()
        driver = self.make_request(driver, 'https://mail.google.com/mail/u/0/#inbox')
        time.sleep(10)
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        links = WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions) \
            .until(
            expected_conditions.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.bog [data-legacy-last-message-id]')))
        values = []
        all_links = []

        for i in range(len(links)):
            try:
                employee_id = "-".join(re.findall("[0-9]+", links[i].text))
                print(employee_id)
                if employee_id:
                    link = '{}{}'.format(self.base_url, links[i].get_attribute('data-legacy-thread-id'))
                    all_links.append(link)
                    self.employee_id.append(employee_id)
                else:
                    continue
            except:
                continue
        driver.quit()
        print(self.employee_id)
        for link, id in zip(all_links, self.employee_id):
            driver = self.create_driver()
            driver = self.make_request(driver, link)
            time.sleep(5)
            # # item = dict()
            if len(self.get_elements(driver, 'span.g3')) > 0:
                date = self.get_elements(driver, 'span.g3')[0].get_attribute('title')
            else:
                date = ''
            raw_body = driver.find_element_by_css_selector('body ').text.replace("\n", ' ')
            try:
                body = driver.find_element_by_css_selector('.gt [dir="ltr"]').text
            except NoSuchElementException:
                self.logger.info("No such element at body")
            values.append([date, raw_body, id, body])
            # driver.execute_script('window.history.go(-1)')
            driver.quit()
            time.sleep(3)

        # insert data into  Google Sheet
        for value in values:
            gc = gspread.service_account(filename='../creds.json')
            # Open a sheet from a spreadsheet in one go
            wks = gc.open("my_sheet").sheet1
            wks.append_row(value)


gm = GmailScraper()
gm.parse()
