import requests
import base64
import json
import time

token_url = "https://accounts.spotify.com/api/token"

def read_config():
  with open("config.json","r") as f:
    config_dict = json.load(f)

  cid = config_dict["id"]
  secret = config_dict["secret"]
  user = config_dict["user"]
  
  return cid, secret, user

def get_encoded_client_secret(client, secret):
  encoded_id_secret = base64.b64encode((client+':'+secret).encode('ascii'))
  return encoded_id_secret.decode("ascii")

def refresh_auth(refresh_token, client_secret, json_fname):
  url = "https://accounts.spotify.com/api/token"
  
  headers={"authorization":"Basic " + client_secret}
  data = {"grant_type":"refresh_token", "refresh_token":refresh_token}
  
  r = requests.post(url,headers=headers,data=data)
  
  r.raise_for_status()
  
  #read in current cached config
  auth, expire, refresh, tok_type = get_cached_auth(json_fname)
  
  #read response
  r_json = json.loads(r.text)
  auth, tok_type, expires, refresh_temp = read_auth_response(r_json)
  
  if (refresh_temp is not None):
    refresh = refresh_temp
  
  #update cached auth info
  write_cached_auth(auth, expires, tok_type, refresh, json_fname)
  
  return auth



#auth, expire, refresh, tok_type
def get_cached_auth(json_fname):
  with open(json_fname, "r") as f:
    auth_dict = json.load(f)
  
  return (auth_dict["auth"]["value"], auth_dict["auth"]["expires"], auth_dict["refresh"], auth_dict["type"])

def read_auth_response(r_json):
  auth = r_json["access_token"]
  tok_type = r_json["token_type"]
  expires = r_json["expires_in"] + int(time.time())
  
  refresh = r_json["refresh_token"] if "refresh_token" in r_json else None
  
  return auth, tok_type, expires, refresh

def write_cached_auth(auth, expires, tok_type, refresh, json_fname):
  auth_dict = {}
  auth_dict["auth"] = {}
  auth_dict["auth"]["value"] = auth
  auth_dict["auth"]["expires"] = expires
  auth_dict["refresh"] = refresh
  auth_dict["type"] = tok_type
  
  with open(json_fname, "w") as f:
    json.dump(auth_dict, f, indent=2)
