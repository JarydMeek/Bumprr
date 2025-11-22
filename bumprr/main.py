import tomllib
import time

# Local imports
from config import get_config
from api import fetch_data

print("Starting Bumprr...")

print("Checking config file...")

config = get_config()


try:
    poll_interval = float(config["poll_interval"])
except (ValueError, TypeError):
    print(f"Error: poll_interval must be a number, got {config['poll_interval']}")
    exit(1)

print("Config file loaded successfully.")

while True:
    try:

        # Main logic would go here

        time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(poll_interval)