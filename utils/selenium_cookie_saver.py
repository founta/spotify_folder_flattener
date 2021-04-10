from seleniumwire import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json

from common import update
update()

from inc import constants

options = webdriver.ChromeOptions()
options.binary_location = constants.chrome
chrome_driver_binary = constants.chrome_driver
driver = webdriver.Chrome(chrome_driver_binary, options=options)

driver.get('https://open.spotify.com')


input("Press enter in this window after logging into open.spotify.com: ")


cookie_names_to_save = ["sp_t", "sp_key", "sp_dc"]
cookie_fields_to_remove = ["expiry"]

cookies = driver.get_cookies()
cookies_to_save = []

for cookie in cookies:
  if cookie["name"] in cookie_names_to_save:
    for field in cookie_fields_to_remove:
      cookie.pop(field, None)
    cookies_to_save.append(cookie)

with open(constants.cookie_json, "w") as f:
  json.dump({"cookies":cookies_to_save}, f, indent=2)

driver.quit()
