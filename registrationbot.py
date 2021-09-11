from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from proxy_connection import check_proxy_connection
import os
import time
import pytz
from datetime import datetime
import logging

tz = pytz.timezone('Europe/Warsaw')

# from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(ChromeDriverManager().install())

USER_EMAIL = os.environ.get('USER_EMAIL')
USER_PASSWORD = os.environ.get('USER_PASSWORD')

login_host = "https://kolejka-wsc.mazowieckie.pl/rezerwacje/pol/login"
chose_localization_host = "https://kolejka-wsc.mazowieckie.pl/rezerwacje/#loc_2"
reservation_host = "https://kolejka-wsc.mazowieckie.pl/rezerwacje/opmenus/terms/200092/200156"

def check_exists_by_xpath(browser, xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def make_full_screenshot(browser, on=False):
    if on:
        date_created = datetime.now(tz).strftime("%Y_%m_%d-%I:%M:%S%p")
        page_title = browser.title
        screenshot_name = page_title.translate({ord(c): None for c in '!@#$/: '})
        screenshot_name_datestamp = f"{date_created}_{screenshot_name}"
        screenshot_path = f'./screenshots/{screenshot_name_datestamp}.png'

        el = browser.find_element(By.TAG_NAME, 'body')
        el.screenshot(screenshot_path)

        logging.info(f'Screenshot: {screenshot_name}')


def registration(headless=False, proxy_ip_port="direct://", make_screenshot=True, logging_level=logging.DEBUG):

    logging.basicConfig(level=logging_level, filename='data.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

    logging.info("----------START----------\n")
    
    logging.info(f'New date are avalable: {make_screenshot}')

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"

    if proxy_ip_port == "proxy.voip.plus:8080":
        logging.info(f'Connection with proxy: {proxy_ip_port}')
        proxy_checked=False
        while not proxy_checked:
            server, str_port = proxy_ip_port.split(":")
            port = int(str_port)
            proxy_checked=check_proxy_connection(server, port, logging_level=logging_level)
        logging.info("Proxy connected Succesfully\n")     

    options = webdriver.ChromeOptions()
    options.headless = headless
    # options.add_argument("--no-first-run") # undetected_chromedriver.v2 
    # options.add_argument("--no-service-autorun") # undetected_chromedriver.v2 
    options.add_argument("user-data-dir=chrome_selenium_profile")
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--ignore-certificate-errors") # browser shows it has no this flag
    # options.add_argument("--allow-running-insecure-content")
    # options.add_argument("--disable-extensions")
    options.add_argument(f'--proxy-server={proxy_ip_port}') # direct://
    if proxy_ip_port == "direct://":
        options.add_argument("--proxy-bypass-list=*")
    else:
        logging.info(f'Connecting with Proxy: {proxy_ip_port}')
    options.add_argument("--start-maximized")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--no-sandbox") # browser shows it has no this flag
    
    chrome_service = Service(executable_path="./chromedriver")
    browser = webdriver.Chrome(service=chrome_service, options=options)

    
    with browser:

        logging.info("Registration are started\n")

        logging.info("Enter Login page")
        browser.get(login_host)

        xpath=f"//li[@class='logo menu-acc-control']/a[@class='dropdown-button']/p[contains(text( ), '{USER_EMAIL}')]"
        user_is_logged = check_exists_by_xpath(browser, xpath)

        logging.info(f'User are logged: {user_is_logged}')
        
        if not user_is_logged:

            logging.info("Trying to login")

            # Take full page screenshot
            make_full_screenshot(browser, on=make_screenshot)

            time.sleep(1)

            email_field = browser.find_element(By.ID, "UserEmail")
            email_field.send_keys(USER_EMAIL)

            time.sleep(1)

            password_field = browser.find_element(By.ID, "UserPassword")
            password_field.send_keys(USER_PASSWORD)

            time.sleep(1)

            submit_btn = browser.find_element(By.XPATH, "//input[@value='Zaloguj']")
            submit_btn.click()

            logging.info("User are logged successfully\n")

            make_full_screenshot(browser, on=make_screenshot)

        browser.get(chose_localization_host)

        time.sleep(2)

        browser.get(reservation_host)

        time.sleep(2)

        accept_terms = browser.find_element(By.XPATH, "//form[@id='customForm']/p/label[@for='terms']")
        accept_terms.click()
        accept_btn = browser.find_element(By.ID, "btn")
        accept_btn.click()

        all_acceptable_days = browser.find_elements(By.XPATH, "//div[starts-with(@id, 'zabuto_calendar_')][@class='day good']")
        actual_registration_date = all_acceptable_days[-1].text
        all_acceptable_days[-1].click()

        make_full_screenshot(browser, on=make_screenshot)

        if make_screenshot:
            date_created = datetime.now(tz).strftime("%Y_%m_%d-%I:%M:%S%p")
            page_source_name_datestamp = f"./page_sources/{date_created}_page_source.html"
            with open(page_source_name_datestamp, "w") as f:
                f.write(browser.page_source)
            logging.info(f'New source html file are created: {page_source_name_datestamp}')

        return actual_registration_date


new_registration_date_list = ['18']
make_screenshot = False
max_amount_screenshots = 0
SCREENSHOTS = 6 # interval 10s
counter = 0
while True:
    actual_registration_date = registration(headless=True, proxy_ip_port="proxy.voip.plus:8080", make_screenshot=make_screenshot, logging_level=logging.INFO) # , headless=True, proxy_ip_port="91.149.203.12:3128"

    if not (actual_registration_date in new_registration_date_list):
        new_registration_date_list.append(actual_registration_date)

        max_amount_screenshots = SCREENSHOTS
        logging.info(f'Available date found: {actual_registration_date}')
        logging.info("Waiting for 1s\n")
        time.sleep(1)

    else:
        if counter < max_amount_screenshots:
            make_screenshot = True
            counter += 1
            logging.info(f'Making screenshot set number: {counter}')
            logging.info("Waiting for 10s\n")
            time.sleep(15)

        else:
            logging.info("No new registration date avalable")

            make_screenshot = False
            logging.info("Waiting for 5min\n")
            time.sleep(300)

    logging.info(f'Registration dates chacked: {new_registration_date_list}')