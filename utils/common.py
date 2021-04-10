import sys
import os
from pathlib import Path

def update_path():
  sys.path.insert(1, os.path.join(sys.path[0], '..'))

def update():
  update_path()
  
  from inc import constants
  constants.config_json = Path("../")/constants.config_json
  constants.auth_json = Path("../")/constants.auth_json
  constants.cookie_json = Path("../")/constants.cookie_json
