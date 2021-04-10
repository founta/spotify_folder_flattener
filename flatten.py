import signal
import sys
import argparse
import time

from lib.folder_flattener import FolderFlattener
from lib.spotify_utils import read_config

if __name__ == "__main__":
  #get argument to let user either flatten folders once or persistently
  parser = argparse.ArgumentParser()
  parser.add_argument('--persist', action='store_true', default=False, help="Whether to continuously look for and flatten folders. Default false")
  args = parser.parse_args()
  persist=args.persist
  
  #set up the folder flattener
  cid, secret, user = read_config()
  folder_flattener = FolderFlattener(cid,secret,user)
  
  #set up clean exit on interrupt
  done = False
  def signal_handler(sig, frame):
    done = True
    folder_flattener.stop()
    sys.exit(0)
  signal.signal(signal.SIGINT, signal_handler)
  
  #flatten spotify folders
  while not done:
    folder_flattener.flatten_folders()
    if (not persist):
      done=True
    else:
      time.sleep(2)
  
  folder_flattener.stop()
