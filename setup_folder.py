import os
from config_provider import ConfigService
configService = ConfigService() 
config = configService.config

filename = config["results_filename"]
n_streams = configService.networkConfig["n_streams"]
base_path = config["base_path"]

folder_path = f"{base_path}\\{n_streams}\\{filename}"

if os.path.exists(folder_path):
    os.rmdir(folder_path)
    
os.makedirs(folder_path)
