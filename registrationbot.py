# from selenium import webdriver
import undetected_chromedriver.v2 as uc # module for solwe site Cloudflare security check
# from seleniumwire import webdriver # webdriver for proxy authentication
from selenium.webdriver.common.proxy import Proxy, ProxyType
from time import sleep


class RegistrationBot:
    def __init__(self, host, headless=False, proxy_ip_port="direct://"):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        self.host = host
        self.headless = headless
        self.proxy_ip_port = proxy_ip_port

        self.options = uc.ChromeOptions()
        self.options_user_data_dir = "./profile"
        self.options.headless = self.headless
        self.options.add_argument("--no-first-run")
        self.options.add_argument("--no-service-autorun")
        self.options.add_argument("--password-store=basic")
        self.options.add_argument(f'--user-agent={user_agent}')
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--allow-running-insecure-content")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument(f'--proxy-server={self.proxy_ip_port}') # direct://
        if self.proxy_ip_port == "direct://":
            self.options.add_argument("--proxy-bypass-list=*")
        else:
            print(f'Connecting with Proxy: {self.proxy_ip_port}')
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--no-sandbox")
        print(self.options.arguments)
        
        # if self.proxy_ip_port is not None:
        #     print(f'Connecting with Proxy: {self.proxy_ip_port}')
        #     self.proxy = Proxy()
        #     self.proxy.proxy_type = ProxyType.MANUAL
        #     self.proxy.http_proxy = self.proxy_ip_port
        #     self.proxy.ssl_proxy = self.proxy_ip_port

        #     self.capabilities = uc.DesiredCapabilities.CHROME
        #     self.proxy.add_to_capabilities(self.capabilities)

        #     self.browser = uc.Chrome(options=self.options, desired_capabilities=self.capabilities) # executable_path="./chromedriver", 
        # else:
        #     print("Connecting without Proxy")
        
        self.browser = uc.Chrome(options=self.options)
        
        with self.browser:
            self.browser.get(f'{self.host}')

            sleep(2)
            
            self.screenshot_name = self.browser.title
            print(self.screenshot_name)
            self.screenshot_path = f'./screenshots/{self.screenshot_name}.png'
            print(self.screenshot_path)

            sleep(2)

            # Take full page screenshot
            self.el = self.browser.find_element_by_tag_name('body')
            self.el.screenshot(self.screenshot_path)

            self.browser.quit()        

    
# class RegistrationBotUseProxy(RegistrationBot):
#     def __init__(self, proxy_ip_port):

#         self.proxy_ip_port = proxy_ip_port

#         proxy = Proxy()
#         proxy.proxy_type = ProxyType.MANUAL
#         proxy.http_proxy = self.proxy_ip_port
#         proxy.ssl_proxy = self.proxy_ip_port

#         capabilities = webdriver.DesiredCapabilities.CHROME
#         proxy.add_to_capabilities(capabilities)





RegistrationBot(host="https://whatismyipaddress.com/", headless=False, proxy_ip_port="213.216.67.190:8080") # , headless=True, proxy_ip_port="91.149.203.12:3128"

# https://whatismyipaddress.com/
# https://kolejka-wsc.mazowieckie.pl/rezerwacje/info/queueinfo
# class RegistrationBot2:
#     def __init__(self):
#         self.browser = webdriver.Chrome("./chromedriver")
#         self.browser.get('https://google.com')
#         self.browser.maximize_window()
#         print(self.browser.title)
#         sleep(1)