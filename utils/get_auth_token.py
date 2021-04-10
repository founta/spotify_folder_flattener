import requests
import base64
import json

import argparse


from common import update
update()

from inc import constants
from lib.spotify_utils import write_cached_auth, read_auth_response

parser = argparse.ArgumentParser()
parser.add_argument("--code", type=str, help="The code you get out of performing initial steps")
parser.add_argument("--scope", type=str, default="playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative", help="The scopes we want out of the auth token")
parser.add_argument("--redirect_url", type=str, default="http://localhost", help="A redirect URI for the spotify app")

args = parser.parse_args()
code = args.code
scope = args.scope
redirect = args.redirect_url

with open(constants.config_json, "r") as f:
  config_dict = json.load(f)

cid = config_dict["id"]
secret = config_dict["secret"]
user = config_dict["user"]

encoded_id_secret = base64.b64encode((cid+':'+secret).encode('ascii'))


headers = {"authorization":"Basic " + encoded_id_secret.decode("ascii")}

url="https://accounts.spotify.com/api/token"

grant_type = "authorization_code"

data = {
  "grant_type":grant_type,
  "code":code,
  "redirect_uri":redirect,
  "scope":scope
}

r = requests.post(url, data=data, headers=headers)

r.raise_for_status()

r_json = json.loads(r.text)

print(r_json)


auth, tok_type, expires, refresh = read_auth_response(r_json)

#save the auth info to disk
write_cached_auth(auth, expires, tok_type, refresh)
