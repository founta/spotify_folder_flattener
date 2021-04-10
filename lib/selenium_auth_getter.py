from seleniumwire import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json

import queue
import multiprocessing
import ctypes

from inc import constants

def auth_retrieval_target(stop, shared_dict):
  options = webdriver.ChromeOptions()
  options.binary_location = "/opt/brave.com/brave/brave"
  chrome_driver_binary = "/usr/bin/chromedriver"
  driver = webdriver.Chrome(chrome_driver_binary, options=options)

  driver.get('https://open.spotify.com')
  
  with open(constants.cookie_json, "r") as f:
    cookies = json.load(f)["cookies"]
  
  for cookie in cookies:
    driver.add_cookie(cookie)

  while not stop.is_set():
    reqs = driver.requests.copy()
    del driver.requests
    for request in reqs:
      if "authorization" in request.headers and "spotify" in request.url:
        shared_dict["auth"] = request.headers["authorization"]
    time.sleep(2)
  
  driver.quit()

class WebAuthGetter():
  def __init__(self):
    self.stop_event = multiprocessing.Event()
    
    self.manager = multiprocessing.Manager()
    self.shared_dict = self.manager.dict()
    self.shared_dict["auth"] = "None"
    
    #kick off selenium
    self.proc = multiprocessing.Process(target=auth_retrieval_target, args=(self.stop_event, self.shared_dict))
    self.proc.start()
  
  def get_auth(self):
    return self.shared_dict["auth"]
  
  def stop(self):
    self.stop_event.set()
    self.proc.join()
