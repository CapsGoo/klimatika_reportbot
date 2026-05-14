import os
import yaml
from pathlib import Path
import json

with open("config.yaml", "r") as config_file:
    CONFIG_FILE = yaml.load(config_file, Loader=yaml.Loader)

BOT_CONFIG = CONFIG_FILE["BOT"]
BOT_TOKEN = BOT_CONFIG["TOKEN"]


SERVICE_ACCOUNT_INFO = Path(__file__).parent / "service-account.json"
OAUTH_TOKEN_INFO = Path(__file__).parent / "token.json"
SCOPES = ['https://www.googleapis.com/auth/drive']

folder_config_path = Path(__file__).parent / "folder.json"

with open(folder_config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

FOLDER_ID = config["FOLDER_ID"]