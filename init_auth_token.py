import requests
import argparse

from spotify_utils import *

parser = argparse.ArgumentParser()
parser.add_argument("--scope", type=str, default="playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative", help="The scopes we want out of the auth token")
parser.add_argument("--redirect_url", type=str, default="http://localhost", help="A redirect URI for the spotify app")

args = parser.parse_args()
scope = args.scope
redirect = args.redirect_url

cid, secret, user = read_config()

url = "https://accounts.spotify.com/authorize"

params = {"client_id":cid, "response_type":"code", "redirect_uri":redirect, "scope":scope}

r = requests.get(url, params=params, allow_redirects = True)
r.raise_for_status()

print(r.url)
