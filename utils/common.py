import sys
import os
from pathlib import Path

def update_path():
  sys.path.insert(1, os.path.join(sys.path[0], '..'))

def update():
  update_path()
