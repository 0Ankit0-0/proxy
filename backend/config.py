import os
from pathlib import Path

Base_Dir = Path(__file__).resolve().parent.parent

# Directory structure configuration 
DATA_DIR = Base_Dir /"backend" / "data"
LOGS_DIR = DATA_DIR / "logs"
MODELS_DIR = DATA_DIR / "models"
UPDATES_DIR = DATA_DIR / "updates"
TEMP_DIR = DATA_DIR / "temp"
DB_PATH = DATA_DIR / "duckdb" / "Q_logs.db"

# Ensure directories exist
for directory in [DATA_DIR, LOGS_DIR, MODELS_DIR, UPDATES_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)


# Security configuration
ENCRYTION_KEY = os.getenv("ENCRYPTION_KEY", "default_encryption_key")
SOUP_KEY = os.getenv("SOUP_KEY", "default_soup_key")

# APP Settings
APP_NAME = "Project Quorum"
APP_VERSION = "1.0.0"
DEBUG = True
ALLOWED_HOSTS = ["*"]

 