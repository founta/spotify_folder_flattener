from lib.folder_flattener import FolderFlattener
from lib.spotify_utils import read_config


if __name__ == "__main__":
  cid, secret, user = read_config()
  
  folder_flattener = FolderFlattener(cid,secret,user)
  
  folder_flattener.flatten_folders()
  folder_flattener.stop()
