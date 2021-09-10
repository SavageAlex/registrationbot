from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from proxy_connection import check_proxy_connection
import time
import pytz
from datetime import datetime, timezone

tz = pytz.timezone('Europe/Warsaw')

# from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(ChromeDriverManager().install())

USER_EMAIL = "atalaver@gmail.com"
USER_PASSWORD = "$avageAlexVN2002"

login_host = "https://kolejka-wsc.mazowieckie.pl/rezerwacje/pol/login#loc_2"
reservation_host = "https://kolejka-wsc.mazowieckie.pl/rezerwacje/opmenus/terms/200092/200156"

def check_exists_by_xpath(browser, xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def make_full_screenshot(browser, screenshot_counter=0):
    date_created = datetime.now(tz).strftime("%Y_%m_%d-%I:%M%p")
    page_title = browser.title
    screenshot_name = page_title.translate({ord(c): None for c in '!@#$/: '})
    screenshot_name_datestamp = f"{date_created}_{screenshot_name}"
    print(screenshot_name)
    screenshot_path = f'./screenshots/{screenshot_name_datestamp}.png'
    print(screenshot_path)

    el = browser.find_element(By.TAG_NAME, 'body')
    el.screenshot(screenshot_path)


def registration(headless=False, proxy_ip_port="direct://"):

    screenshot_counter = 0
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"

    if proxy_ip_port == "proxy.voip.plus:8080":
        print(f'Connection with proxy: {proxy_ip_port}')
        proxy_checked=False
        while not proxy_checked:
            server, str_port = proxy_ip_port.split(":")
            port = int(str_port)
            proxy_checked=check_proxy_connection(server, port)
        print("Proxy connected Succesfully")     

    options = webdriver.ChromeOptions()
    options.headless = headless
    # options.add_argument("--no-first-run") # undetected_chromedriver.v2 
    # options.add_argument("--no-service-autorun") # undetected_chromedriver.v2 
    options.add_argument("user-data-dir=chrome_selenium_profile")
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors") # browser shows it has no this flag
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-extensions")
    options.add_argument(f'--proxy-server={proxy_ip_port}') # direct://
    if proxy_ip_port == "direct://":
        options.add_argument("--proxy-bypass-list=*")
    else:
        print(f'Connecting with Proxy: {proxy_ip_port}')
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox") # browser shows it has no this flag
    print(options.arguments)
    
    chrome_service = Service(executable_path="./chromedriver")
    browser = webdriver.Chrome(service=chrome_service, options=options)


    
    with browser:

        browser.get(login_host)

        xpath=f"//li[@class='logo menu-acc-control']/a[@class='dropdown-button']/p[contains(text( ), '{USER_EMAIL}')]"
        print(xpath)
        user_is_logged = check_exists_by_xpath(browser, xpath)

        print(user_is_logged)
        
        if not user_is_logged:

            # Take full page screenshot
            make_full_screenshot(browser)

            time.sleep(1)

            email_field = browser.find_element(By.ID, "UserEmail")
            email_field.send_keys(USER_EMAIL)

            time.sleep(1)

            password_field = browser.find_element(By.ID, "UserPassword")
            password_field.send_keys(USER_PASSWORD)

            time.sleep(1)

            submit_btn = browser.find_element(By.XPATH, "//input[@value='Zaloguj']")
            submit_btn.click()

            make_full_screenshot(browser)

        browser.get(reservation_host)

        make_full_screenshot(browser)

        accept_terms = browser.find_element(By.XPATH, "//form[@id='customForm']/p/label[@for='terms']")
        accept_terms.click()
        accept_btn = browser.find_element(By.ID, "btn")
        accept_btn.click()

        all_acceptable_days = browser.find_elements(By.XPATH, "//div[starts-with(@id, 'zabuto_calendar_')][@class='day good']")
        all_acceptable_days[-1].click()

        make_full_screenshot(browser)


registration(headless=False, proxy_ip_port="proxy.voip.plus:8080") # , headless=True, proxy_ip_port="91.149.203.12:3128"
