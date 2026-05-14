import os
import yaml
from pathlib import Path
import json

with open("config.yaml", "r") as config_file:
    CONFIG_FILE = yaml.load(config_file, Loader=yaml.Loader)

BOT_CONFIG = CONFIG_FILE["BOT"]
BOT_TOKEN = BOT_CONFIG["TOKEN"]



# ========== ЗАГРУЗКА КОНФИГУРАЦИИ ==========
# Загружаем ID папки из folder.json
with open(Path(__file__).parent / "folder.json", 'r', encoding='utf-8') as f:
    config = json.load(f)
    FOLDER_ID = config["FOLDER_ID"]

# Настройки Google Drive API
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent / "token.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
