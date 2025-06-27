import os
import random
import string
from dotenv import load_dotenv, set_key, dotenv_values

# Load existing .env values
load_dotenv()
env_file = '.env'

def generate_api_key(length=32):
    """Generate a random 32-character API key."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def update_env_api_key(new_key):
    """Replace the existing API_KEY in .env with the new key."""
    # Load current .env config
    env_config = dotenv_values(env_file)

    # Remove old API_KEY (if any)
    if 'API_KEY' in env_config:
        print(f"[+] Old API Key Found. Replacing...")

    # Set new API key
    set_key(env_file, 'API_KEY', new_key)
    print(f"[+] API Key Updated in .env")

if __name__ == "__main__":
    print("[*] Generating new 32-character API Key...")
    new_api_key = generate_api_key()
    print(f"[+] New API Key: {new_api_key}")

    update_env_api_key(new_api_key)
    print("[✔] API Key generation completed. Please restart your Flask app to apply the new key.")
