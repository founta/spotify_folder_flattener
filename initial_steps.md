## initial steps:

- these steps are just for getting auth tokens, can be skipped if already have

- make spotify application on their site
  - `https://developer.spotify.com/dashboard/`
- set redirect uri to "http://localhost"
- put client id and secret in config.json
- run `python3 init_auth_token.py`
- go to the url it prints out
  - something like `https://accounts.spotify.com/login?continue=https%3A%2F%2Faccounts.spotify.com%2Fauthorize%3Fclient_id%3D5e58373a7cd44eb483f04301f8c97198%26response_type%3Dcode%26redirect_uri%3Dhttp%253A%252F%252Flocalhost`
  - login on that page
- It will redirect to localhost, copy the code out of the URL
  - url will look like `http://localhost/?code=AQCOqpjnBAyUj8x7BmM3AKaNfH8dy3xUObKphqg7BidH6RXL_KIGFKm55_rIDk9QQ2Mm1rLsu1XeGpmkL1Pf3tNlvH0IahetqGQ6zQM60McKnC8jqC1_6ZlpDw60RrPEc6EdMa3ZX7Cpa9ZEPyTugXUEwbQ`
  - copy the code part
- run `python3 get_auth_token.py` --code=THECODE
  - where THECODE is the code copied earlier
- This will cache the auth token, so these steps shouldn't have to be done again

