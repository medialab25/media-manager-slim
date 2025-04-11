#!/usr/bin/env python3
import os
import json
from app.routes.media import merge_media

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Run merge
try:
    merge_media(config['MEDIA_MERGE'])
    print("Merge completed successfully")
except Exception as e:
    print(f"Error during merge: {str(e)}") 