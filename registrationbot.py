from selenium import webdriver
# from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException, TimeoutException
from proxy_connection import check_proxy_connection
import os
import time
import pytz
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.DEBUG, filename='data.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')


tz_WA = pytz.timezone('Europe/Warsaw')

USER_EMAIL = os.environ.get('USER_EMAIL')
USER_PASSWORD = os.environ.get('USER_PASSWORD')

captcha = "123456"
first_last_name = "Ivanov Mykolaj"
birthday_date = "1992-07-05" #format 'yyyy-mm-dd'
citizenship = "Ukraine"
passport_number = "VD123456"
phone_number = "123456789"
email = USER_EMAIL

reservation_host = "https://kolejka-wsc.mazowieckie.pl/rezerwacje/pol/opmenus/terms/19/200180" #"https://kolejka-wsc.mazowieckie.pl/rezerwacje/opmenus/terms/200092/200156"

registration_type_expected = "Operacja: I - Pobyt obywateli UE"

start_time = "21:40:00"
duration = "00:10:00"


def check_exists_by_xpath(browser, xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except TimeoutException:
        return False
    return True

def make_full_screenshot(browser, on=False):
    if on:
        date_created = datetime.now(tz_WA).strftime("%Y_%m_%d-%I:%M:%S%p")
        page_title = browser.title
        screenshot_name = page_title.translate({ord(c): None for c in '!@#$/: '})
        screenshot_name_datestamp = f"{date_created}_{screenshot_name}"
        screenshot_path = f'./screenshots/{screenshot_name_datestamp}.png'

        el = browser.find_element(By.TAG_NAME, 'body')
        el.screenshot(screenshot_path)

        logging.info(f'Screenshot: {screenshot_name}')

def selenium_browser_setup(headless=False, proxy_ip_port="direct://", make_screenshot=True):

    logging.info("----------START----------\n")

    logging.info(f'Make screenshot is active: {make_screenshot}')

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"

    if proxy_ip_port == "proxy.voip.plus:8080":
        logging.info(f'Connection with proxy: {proxy_ip_port}')
        proxy_checked=False
        while not proxy_checked:
            server, str_port = proxy_ip_port.split(":")
            port = int(str_port)
            proxy_checked=check_proxy_connection(server, port)
        logging.info("Proxy connected Succesfully\n")     

    options = webdriver.ChromeOptions()
    options.headless = headless
    options.add_argument("user-data-dir=chrome_selenium_profile")
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f'--proxy-server={proxy_ip_port}') # direct://
    if proxy_ip_port == "direct://":
        options.add_argument("--proxy-bypass-list=*")
    else:
        logging.info(f'Connecting with Proxy: {proxy_ip_port}')
    options.add_argument("--start-maximized")

    chrome_service = Service(executable_path="./chromedriver")
    browser = webdriver.Chrome(service=chrome_service, options=options)
    return browser

def check_for_user_is_logged(browser, host, email, password, make_screenshot):
    logging.info("Enter page")
    browser.get(host)

    xpath=f"//li[@class='logo menu-acc-control']/a[@class='dropdown-button']/p[contains(text( ), '{email}')]"

    while True:
        try:
            WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.XPATH, xpath))) # check_exists_by_xpath(browser, xpath)
            user_is_logged = True
            logging.info("User are logged!")
            return user_is_logged

        except TimeoutException:
            user_is_logged = False
            logging.warning("User isn't logget in")
    
        if not user_is_logged:

            logging.info("Trying to login")

            # browser.get(login_host)

            # Take full page screenshot
            make_full_screenshot(browser, on=make_screenshot)

            try:
                email_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "UserEmail")))
                email_field.send_keys(email)
            except TimeoutException:
                logging.warning("Can't find email field")
                successful_registration = False
                return successful_registration

            try:
                password_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "UserPassword")))
                password_field.send_keys(password)
            except TimeoutException:
                logging.warning("Can't find password field")
                successful_registration = False
                return successful_registration

            try:
                submit_btn = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@value='Zaloguj']")))
                submit_btn.click()
            except TimeoutException:
                logging.warning("Can't find submit button")
                successful_registration = False
                return successful_registration

            logging.info("User are logged successfully\n")

            make_full_screenshot(browser, on=make_screenshot)

def find_available_dates(browser, host, registration_type_expected, make_screenshot):
    browser.get(host)

    # Accept terms

    try:
        accept_terms = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='customForm']/p/label[@for='terms']")))
        accept_terms.click()
    except TimeoutException:
        logging.warning("Can't find accept terms check box")
        successful_registration = False
        return successful_registration
    try:
        accept_btn =  WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "btn")))
        accept_btn.click()
    except TimeoutException:
        logging.warning("Can't find accept terms button")
        successful_registration = False
        return successful_registration
    # Confirm registration type

    try:
        xpath = f"//div[@class='container']/div[@class='row']/div[contains(@class, 'col') and contains(@class, 's12')]/h4[contains(@class, 'primary-text')][contains(text( ), '{registration_type_expected}')]"
        registration_type = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        logging.info("Registration type comfirmed")
    except TimeoutException:
        logging.warning("Can't find registration type text")
        successful_registration = False
        return successful_registration

    # Finding actual available dates

    logging.info("Locking for dates")

    try:
        all_available_days = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[starts-with(@id, 'zabuto_calendar_')][@class='day good']")))
        make_full_screenshot(browser, on=make_screenshot)
        logging.info("Avalible dates are exists")
        break_out_flag = False
        for day in all_available_days[::-1]:
            day.click()
            try:
                all_available_terms = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@id, 'dateContent')]/ul[contains(@class, 'smartColumns')]/li/div[contains(@class, 'block')]/a[contains(@class, 'confirm') and contains(@class, 'form')]")))
                logging.info("Avalible terms are exists")
                make_full_screenshot(browser, on=make_screenshot)
                for term in all_available_terms:
                    term.click()
                    break_out_flag = True
                    break
            except TimeoutException:
                logging.warning("Can't find available terms")
                successful_registration = False
                return successful_registration
            if break_out_flag:
                break
    except TimeoutException:
        logging.warning("Can't find available dates")
        successful_registration = False
        return successful_registration
    
    make_full_screenshot(browser, on=make_screenshot)

    # Fill out registration form

    logging.info("Filleng registration form")

    form_are_submitted = False

    captcha_image = ""

    try:
        captcha_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'form')]/div[contains(@class, 'input') and contains(@class, 'text')]/input[contains(@id, 'captcha')]")))
        captcha_field.send_keys(captcha)
    except TimeoutException:
        logging.warning("Can't find captcha field")
        successful_registration = False
        return successful_registration

    try:
        first_last_name_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='customForm']/div[@id='text_0']/input[@name='text_0']")))
        first_last_name_field.send_keys(first_last_name)
    except TimeoutException:
        logging.warning("Can't find first last name field")
        successful_registration = False
        return successful_registration
    try:
        birthday_date_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='customForm']/div[@id='text_4']/input[@id='selDate_text_4']")))
        birthday_date_field.click()
        try:
            birthday_month = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='picker__calendar-container']/div[@class='picker__header']/select[contains(@class, 'picker__select--month')]")))
            birthday_month_select_list = Select(birthday_month)
            birthday_month_select_list.select_by_visible_text("Grudzień")
        except TimeoutException:
            logging.warning("Can't find birthday month")
            successful_registration = False
            return successful_registration
        try:
            birthday_year = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='picker__calendar-container']/div[@class='picker__header']/select[contains(@class, 'picker__select--year')]")))
            birthday_year_select_list = Select(birthday_year)
            birthday_year_select_list.select_by_visible_text("1985")
        except TimeoutException:
            logging.warning("Can't find birthday year")
            successful_registration = False
            return successful_registration
        try:
            birthday_dates = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='picker__calendar-container']/table[@class='picker__table']/tbody/tr/td/div[contains(@class, 'picker__day') and contains(@class, 'picker__day--infocus')]")))
            for birthday_date in birthday_dates:
                if birthday_date.text == "15":
                    birthday_date.click()
                    try:
                        birthday_date_submit_btn = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='picker__footer']/button[contains(@class, 'btn-flat') and contains(@class, 'picker__close')]")))
                        birthday_date_submit_btn.click()
                        break
                    except TimeoutException:
                        logging.warning("Can't find birthday date submit button")
                        successful_registration = False
                        return successful_registration
        except TimeoutException:
            logging.warning("Can't find birthday date")
            successful_registration = False
            return successful_registration
    except TimeoutException:
        logging.warning("Can't find birthday date field")
        successful_registration = False
        return successful_registration

    try:
        citizenship_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='customForm']/div[@id='text_5']/input[@name='text_5']")))
        citizenship_field.send_keys(citizenship)
    except TimeoutException:
        logging.warning("Can't find citizenship field")
        successful_registration = False
        return successful_registration

    try:
        passport_number_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='customForm']/div[@id='text_1']/input[@name='text_1']")))
        passport_number_field.send_keys(passport_number)
    except TimeoutException:
        logging.warning("Can't find passport number field")
        successful_registration = False
        return successful_registration

    try:
        phone_number_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='customForm']/div[@id='text_2']/input[@name='text_2']")))
        phone_number_field.send_keys(phone_number)
    except TimeoutException:
        logging.warning("Can't find phone number field")
        successful_registration = False
        return successful_registration

    try:
        email_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='customForm']/div[@id='text_3']/input[@name='text_3']")))
        email_field.send_keys(email)
    except TimeoutException:
        logging.warning("Can't find email field")
        successful_registration = False
        return successful_registration

    make_full_screenshot(browser, on=make_screenshot)

    try:
        submit_btn = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='customForm']/button[@id='submit']")))
        submit_btn.click()
        form_are_submitted = True
    except TimeoutException:
        logging.warning("Can't find submit button")
        successful_registration = False
        return successful_registration

    logging.info("Form are submitted")

    make_full_screenshot(browser, on=make_screenshot)

    if make_screenshot:
        date_created = datetime.now(tz_WA).strftime("%Y_%m_%d-%I:%M:%S%p")
        page_source_name_datestamp = f"./page_sources/{date_created}_page_source.html"
        with open(page_source_name_datestamp, "w") as f:
            f.write(browser.page_source)
        logging.info(f'New source html file are created: {page_source_name_datestamp}')

    time.sleep(10)

    return form_are_submitted

def registration(browser, host, registration_type_expected, email, password, make_screenshot):
    if check_for_user_is_logged(browser, host, email, password, make_screenshot):
        last_added_date = find_available_dates(browser, host, registration_type_expected, make_screenshot)
    actual_registration_date = last_added_date
    registration_result = False
    return registration_result, actual_registration_date

def scheduled_run_registration(start_time, running_time, host, registration_type_expected, email, password, headless, proxy_ip_port, make_screenshot):
    registtration_success = False
    today_start = datetime.now(tz_WA).replace(hour=int(start_time[0:2]), minute=int(start_time[3:5]), second=int(start_time[6:8]))
    today_stop = today_start + timedelta(hours=int(running_time[0:2]), minutes=int(running_time[3:5]), seconds=int(running_time[6:8]))

    while not registtration_success:
        now = datetime.now(tz_WA)        
        logging.info(f'Current time: {now}')
        logging.info(f'Schedulled start time: {today_start} and stop time: {today_stop}')

        if today_start <= now <= today_stop:
            logging.info("Schedelled Start")
            browser = selenium_browser_setup(headless, proxy_ip_port, make_screenshot)
            with browser:
                registtration_success, actual_registration_date = registration(browser, host, registration_type_expected, email, password, make_screenshot)
        logging.info("Another schedule waiting loop, wait 1s")
        time.sleep(1)
    return registtration_success, actual_registration_date

actual_registration_date = scheduled_run_registration(start_time=start_time, running_time=duration, host=reservation_host, registration_type_expected=registration_type_expected, email=USER_EMAIL, password=USER_PASSWORD, headless=True, proxy_ip_port="proxy.voip.plus:8080", make_screenshot=True)