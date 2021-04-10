import requests
import base64
import json

import time

from .selenium_auth_getter import WebAuthGetter

class FolderReader():
  def __init__(self, user):
    self.webauth_getter = WebAuthGetter()
    self.user = user
  
  def get_raw_rootlist(self, timeout=60):
    url = "https://spclient.wg.spotify.com/playlist/v2/user/" + self.user + "/rootlist"
    start = time.time()
    done = False
    
    while float(time.time() - start) < timeout:
      try:
        auth = self.get_webauth()
        headers={"authorization": auth, "accept":"application/json"}
        
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        done = True
        break
      except requests.exceptions.HTTPError:
        time.sleep(0.5)
    
    if not done:
      raise RuntimeError("Could not get the root list in %.2f seconds" % (timeout))
    
    return (r.text,r)
  
  def stop(self):
    self.webauth_getter.stop()
  
  def get_webauth(self, timeout=20):
    start = time.time()
    
    webauth = None
    while float(time.time() - start) < timeout:
      new_auth = self.webauth_getter.get_auth()
      if new_auth != "None":
        webauth = new_auth
        break
      else:
        time.sleep(0.5)
    
    if webauth is None:
      raise RuntimeError("Could not get webauth in %.2fs" % (timeout))
    return webauth
  
  def get_flattened_folders(self):
    rootlist, r = self.get_raw_rootlist()
    
    root_json = json.loads(rootlist)
    root_contents = root_json["contents"]
    
    #TODO not sure how to deal with this. You probably specify the offset, desired num 
    #items in the request to the rootlist endpoint. Not yet an issue for my use case
    if (root_contents["truncated"]):
      print("Warning: truncated root list")
    
    items = root_contents["items"]
    
    #for each folder, put playlist URIs in a flattened list
    flattened_folders = []
    folder_names = []
    current_folder = None
    current_folder_id = None
    for item in items:
      uri = item["uri"]
      uri_split = uri.split(":")
      
      #root folder start
      if "start-group" in uri and current_folder is None:
        current_folder_id = uri_split[-2]
        #TODO are there other special character replacements?
        folder_names.append(requests.utils.unquote(uri_split[-1].replace("+"," ")))
        current_folder = []
      
      #playlist in folder
      if (current_folder is not None) and ("playlist" in uri):
        current_folder.append(uri)
      
      #root folder end
      if (current_folder is not None) and ("end-group" in uri) and (uri_split[-1] == current_folder_id):
        flattened_folders.append(current_folder)
        current_folder = None
    
    return flattened_folders, folder_names

if __name__ == "__main__":
  from spotify_utils import *
  cid, secret, user = read_config()
  
  folder_reader = FolderReader(user)
  
  flattened_folders, folder_names = folder_reader.get_flattened_folders()
  print(flattened_folders)
  print(folder_names)
  
  folder_reader.stop()
