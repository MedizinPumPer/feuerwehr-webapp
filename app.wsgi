import sys
import os
import json

# Path to your Flask application
sys.path.insert(0, '/var/www/feuerwehr-webapp')

# Load configuration from JSON file
config_path = os.path.join('/var/www/feuerwehr-webapp', 'config.json')
with open(config_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# Set environment variables
for key, value in config.items():
    if isinstance(value, str):
        os.environ[key] = value.encode('ascii', 'ignore').decode('ascii')
    elif isinstance(value, list):
        os.environ[key] = ','.join(value).encode('ascii', 'ignore').decode('ascii')

# Import your Flask application
from app import app as application
