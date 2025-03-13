"""
Get the Cloudflare token
"""
import os
import dotenv as env

env.load_dotenv()

CF_API_TOKEN = os.getenv("CF_API_TOKEN")

if not CF_API_TOKEN:
    raise ValueError("Missing or invalid API token.")