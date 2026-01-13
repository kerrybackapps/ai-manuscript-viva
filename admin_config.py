"""
Admin Control Panel Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Admin authentication
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'changeme123')

# Prompts directory
PROMPTS_DIR = 'prompts'

# Ensure prompts directory exists
os.makedirs(PROMPTS_DIR, exist_ok=True)
