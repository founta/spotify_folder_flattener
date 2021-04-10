from pathlib import Path

config_dir = Path(__file__).resolve().parent / ".." / "config"
config_dir = config_dir.resolve()

cookie_json = config_dir / "spcookies.json"
config_json = config_dir / "config.json"
auth_json = config_dir / "token_info.json"

chrome="/opt/brave.com/brave/brave"
chrome_driver="/usr/bin/chromedriver"
