# Prereqs
- python3.7+
- poetry (https://python-poetry.org/)
- Chrome-based web browser
- Chrome driver (https://chromedriver.chromium.org/downloads)

# Installation

## Update configuration
Set the path to your chrome-based browser executable and the driver in `inc/constants.py`

## Get authentication information for the spotify web player
This is for getting a user's playlist folder structure (have to hit an endpoint only the web player can access)
- Run `poetry run python3 utils/selenium_cookie_saver.py`
- log into the Spotify web player that pops up in a new chrome window
- hit enter in the terminal window running the python script

## Get an initial authentication token from Spotify
This is for creating and deleting playlists
- make a spotify application on their site
  - `https://developer.spotify.com/dashboard/`
- set redirect uri to "http://localhost"
- put client id and secret in config/config.json
  - also put the desired username in config.json
- run `poetry run python3 utils/init_auth_token.py`
- go to the url it prints out
  - something like `https://accounts.spotify.com/login?continue=https%3A%2F%2Faccounts.spotify.com%2Fauthorize%3Fclient_id.....`
  - login on that page
- It will redirect to localhost, copy the code out of the URL
  - url will look like `http://localhost/?code=xxxxxxx`
  - copy the code part
- run `poetry run python3 utils/get_auth_token.py --code=THECODE`
  - where THECODE is the code copied earlier
- This will cache the auth token, so these steps shouldn't have to be done again

# Running

## Once
Create a playlist that contains all tracks in each folder for a user
`poetry run python3 flatten.py`

## Persistent
Create a playlist that contains all tracks in each folder for a user, and monitor for updates to the structure of the folders over time
`poetry run python3 flatten.py --persist`

## As a system service
Build the script:
`cd system && python3 make_system_service_script.py`

Install the script:
`sudo cp spotify_folder_flattener.service /etc/systemd/system`

Run the service:
`sudo systemctl start spotify_folder_flattener.service`

Run on startup:
`sudo systemctl enable spotify_folder_flattener.service`
