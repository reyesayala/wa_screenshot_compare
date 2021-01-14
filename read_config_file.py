"Reads the configuration file and stores it in an object"

import configparser
from config import load_config
 

load_config()
import config
print("The settings file has been read")