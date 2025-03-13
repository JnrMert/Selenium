from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from config import FIREFOX_PROFILE, FIREFOX_BINARY


### BURADA KULLANILACAK DRIVER AYARLARI YAPILDI

def setup_driver():
    from selenium.webdriver.firefox.options import Options
    firefox_options = Options()
    firefox_options.binary_location = FIREFOX_BINARY
    firefox_options.add_argument('-profile')
    #firefox_options.add_argument('--headless')
    firefox_options.add_argument(FIREFOX_PROFILE)
    service = Service("./geckodriver.exe")
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.maximize_window()
    return driver
