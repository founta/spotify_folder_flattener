import requests
import base64
import json

import time

from folder_reader import FolderReader
from spotify_utils import *


class FolderFlattener():
  def __init__(self, cid, secret, user):
    self.folder_reader = FolderReader(user)
    self.cid = cid
    self.secret = secret
    self.user = user
    
    self.auth, self.expire, self.refresh, self.tok_type = get_cached_auth()
    
    self.encoded_id_secret = get_encoded_client_secret(cid, secret)
    
    self.watermark = "+f+: "
  
  def try_with_refresh(self,func,*args,**kwargs):
    try:
      ret = func(*args, **kwargs)
    except requests.exceptions.HTTPError:
      self.auth = refresh_auth(self.refresh, self.encoded_id_secret)
      ret = func(*args, **kwargs)
    return ret
  
  def stop(self):
    self.folder_reader.stop()
  
  def get_track_count(self, playlist_id):
    header = {"authorization": self.tok_type + " " + self.auth}
    params = {"fields":"total"}
    url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
    
    r = requests.get(url, params=params, headers=header)
    r.raise_for_status()
    return json.loads(r.text)["total"]
  
  def get_track_uris(self, playlist_id, count, offset=0):
    header = {"authorization": self.tok_type + " " + self.auth}
    params = {"limit":count, "offset":offset, "fields":"items(track.id,track.uri)"}
    url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
    
    r = requests.get(url, params=params, headers=header)
    r.raise_for_status()
    
    rj = json.loads(r.text)
    return [item["track"]["uri"] for item in rj["items"]]
  
  def get_all_track_uris_in_playlist(self, playlist_id, chunksize=100):
    num_tracks = self.try_with_refresh(self.get_track_count, playlist_id)
    
    track_uris = []
    tracks_received = 0
    while tracks_received < num_tracks:
      ids = self.try_with_refresh(self.get_track_uris, playlist_id,chunksize,tracks_received)
      for tid in ids:
        track_uris.append(tid)
      tracks_received += len(ids)
      
      time.sleep(0.05)
    
    return track_uris
  
  def get_playlist_count(self):
    header = {"authorization": self.tok_type + " " + self.auth}
    params = {"limit":0, "offset":0}
    url = "https://api.spotify.com/v1/me/playlists"
    
    r = requests.get(url, params=params, headers=header)
    r.raise_for_status()
    return json.loads(r.text)["total"]
  
  def get_playlists(self, count, offset=0):
    header = {"authorization": self.tok_type + " " + self.auth}
    params = {"limit":count, "offset":offset}
    url = "https://api.spotify.com/v1/users/"+self.user+"/playlists"
    
    r = requests.get(url, params=params, headers=header)
    r.raise_for_status()
    return json.loads(r.text)
  
  def get_user_id(self):
    header = {"authorization": self.tok_type + " " + self.auth}
    
    url = "https://api.spotify.com/v1/me"
    r = requests.get(url, headers=header)
    r.raise_for_status()
    return json.loads(r.text)["id"]
    
  def create_playlist(self, playlist_name):
    headers = {"authorization": self.tok_type + " " + self.auth}
    body = {"name":playlist_name, "description":""}
    url = "https://api.spotify.com/v1/users/"+self.get_user_id()+"/playlists"
    
    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
    return json.loads(r.text)["id"]

  def delete_playlist(self, playlist_id):
    headers = {"authorization": self.tok_type + " " + self.auth}
    url = "https://api.spotify.com/v1/playlists/"+playlist_id+"/followers"
    
    r = requests.delete(url, headers=headers)
    r.raise_for_status()
    return
  
  def add_tracks_to_playlist(self,playlist_id,track_uris):
    headers = {"authorization": self.tok_type + " " + self.auth}
    url = "https://api.spotify.com/v1/playlists/"+playlist_id+"/tracks"
    data = {"uris":track_uris}
    
    r = requests.post(url, headers=headers, json=data)
    r.raise_for_status()
    return
  
  def delete_tracks_from_playlist(self,playlist_id,track_uris):
    headers = {"authorization": self.tok_type + " " + self.auth}
    url = "https://api.spotify.com/v1/playlists/"+playlist_id+"/tracks"
    data = {"uris":track_uris}
    
    r = requests.delete(url, headers=headers, json=data)
    r.raise_for_status()
    return
  
  #add or delete tracks
  def manipulate_tracks_in_playlist(self, playlist_id, track_uris, delete=False, chunksize=100):
    tracks_added = 0
    num_tracks = len(track_uris)
    while tracks_added < num_tracks:
      tracks_this_time = []
      for i in range(min(chunksize, num_tracks-tracks_added)):
        tracks_this_time.append(track_uris[tracks_added+i])
      tracks_added += len(tracks_this_time)
      
      if delete:
        self.try_with_refresh(self.delete_tracks_from_playlist, playlist_id, tracks_this_time)
      else:
        self.try_with_refresh(self.add_tracks_to_playlist, playlist_id, tracks_this_time)
    return

  def check_for_playlist(self, playlist_name, chunksize=10):
    num_playlists = self.try_with_refresh(self.get_playlist_count)
    
    playlists_checked = 0
    playlist_found = False
    playlist_id = None
    while playlists_checked < num_playlists:
      playlists = self.try_with_refresh(self.get_playlists, chunksize,playlists_checked)
      items = playlists["items"]
      
      for item in items:
        name = item["name"]
        if name == playlist_name:
          playlist_found = True
          playlist_id = item["id"]
          break
      playlists_checked += len(items)
      if playlist_found:
        break
    return playlist_found,playlist_id
  
  def flatten_folders(self):
    #get playlists ids in folders
    playlist_groups, folder_names = self.folder_reader.get_flattened_folders()
    
    for i in range(len(playlist_groups)):
      group = playlist_groups[i]
      name = folder_names[i]
      if len(group) == 0:
        continue
      
      #get all track uids
      track_uris = []
      for playlist_id in group:
        track_uris += self.get_all_track_uris_in_playlist(playlist_id.split(":")[-1])
      
      flattened_playlist_name = self.watermark + name
      
      exists,flattened_id = self.check_for_playlist(flattened_playlist_name)
      
      #check if the flattened playlist exists
      #if so, check if the flattened contents have changed
      #if they changed, update the contents of the flattened playlist
      
      #if it doesn't exist or the contents changed:
      #create the flattened playlist
      #add all track ids to the flattened playlist
      if not exists:
        flattened_id = self.try_with_refresh(self.create_playlist,flattened_playlist_name)
        self.manipulate_tracks_in_playlist(flattened_id,track_uris,delete=False)
      else:
        existing_track_uris = self.get_all_track_uris_in_playlist(flattened_id)
        discrepancies = list(set(track_uris) ^ set(existing_track_uris))
        tracks_to_delete = []
        tracks_to_add = []
        for uri in discrepancies:
          if uri in existing_track_uris:
            tracks_to_delete.append(uri)
          else:
            tracks_to_add.append(uri)
        self.manipulate_tracks_in_playlist(flattened_id,tracks_to_add,delete=False)
        self.manipulate_tracks_in_playlist(flattened_id,tracks_to_delete,delete=True)

if __name__ == "__main__":
  cid, secret, user = read_config()
  
  folder_flattener = FolderFlattener(cid,secret,user)
  
  #print(folder_flattener.get_playlists(0))
  #print(folder_flattener.check_for_playlist("alterlnative"))
  #print(folder_flattener.get_user_id())
  #print(folder_flattener.create_playlist(folder_flattener.watermark + "test"))
  folder_flattener.flatten_folders()
  folder_flattener.stop()
#  print(folder_flattener.get_track_uris("4GeOxfkus4918LolQq3822", 2,1))
#  print(folder_flattener.get_all_track_uris_in_playlist("4GeOxfkus4918LolQq3822"))
