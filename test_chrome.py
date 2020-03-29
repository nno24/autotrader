from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--kiosk")

driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get('https://google.com')